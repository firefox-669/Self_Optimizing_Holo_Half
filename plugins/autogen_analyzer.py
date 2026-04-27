"""
AutoGen 框架专用的链路采集与分析插件

此插件通过解析 AutoGen 生成的对话日志来提取执行链路，无需修改 AutoGen 任何代码。

AutoGen 日志结构:
- 支持 GroupChat 模式的对话记录
- 支持 ConversableAgent 的消息历史
- 支持 JSON/JSONL 格式的日志导出
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from .base import BaseAnalyzer, ExecutionStep


class AutoGenAnalyzer(BaseAnalyzer):
    """AutoGen 日志分析器"""
    
    @property
    def name(self) -> str:
        return "autogen_analyzer"

    def is_compatible(self, source_path: str) -> bool:
        """判断该插件是否能处理指定路径的数据源"""
        path = Path(source_path)
        
        # 检查是否是 AutoGen 日志文件或目录
        if path.is_dir():
            # 检查是否有 AutoGen 特有的文件
            has_chat_log = any(f.name in ['chat_log.json', 'group_chat.json', 'messages.jsonl'] 
                             for f in path.rglob('*.json*'))
            return has_chat_log
        
        # 如果是文件，检查扩展名
        if path.is_file():
            return path.suffix.lower() in ['.json', '.jsonl']
        
        return False

    def collect_trace(self, source_path: str) -> List[ExecutionStep]:
        """
        从 AutoGen 日志中收集执行链路
        
        Args:
            source_path: 日志文件或目录路径
            
        Returns:
            执行步骤列表
        """
        steps = []
        path = Path(source_path)
        
        global_step_id = 0
        
        # 确定要处理的文件列表
        if path.is_file():
            files_to_process = [path]
        else:
            # 查找目录下所有 JSON/JSONL 文件
            files_to_process = list(path.rglob('*.json')) + list(path.rglob('*.jsonl'))
            # 按修改时间排序，优先处理最新的
            files_to_process = sorted(files_to_process, key=lambda x: x.stat().st_mtime, reverse=True)
        
        print(f"🔍 找到 {len(files_to_process)} 个日志文件")
        
        for log_file in files_to_process:
            try:
                file_steps = self._parse_log_file(log_file, global_step_id)
                steps.extend(file_steps)
                global_step_id += len(file_steps)
                
                if file_steps:
                    print(f"   ✅ 成功解析 {log_file.name}: 提取 {len(file_steps)} 步")
                    
            except Exception as e:
                print(f"   ⚠️  解析 {log_file.name} 失败: {e}")
        
        # 按时间戳排序
        steps.sort(key=lambda x: x.timestamp if x.timestamp else 0)
        
        # 重新分配连续的 Step ID
        for i, step in enumerate(steps):
            step.step_id = i + 1
        
        print(f"   ✅ 总计提取 {len(steps)} 步")
        
        return steps
    
    def _parse_log_file(self, log_file: Path, start_id: int) -> List[ExecutionStep]:
        """解析单个日志文件"""
        steps = []
        step_id = start_id
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                if log_file.suffix == '.jsonl':
                    # JSONL 格式：每行一个 JSON 对象
                    lines = f.readlines()
                    for line in lines:
                        if not line.strip():
                            continue
                        try:
                            message = json.loads(line)
                            step = self._extract_step_from_message(message, step_id + 1, log_file)
                            if step:
                                steps.append(step)
                                step_id += 1
                        except json.JSONDecodeError:
                            continue
                else:
                    # JSON 格式
                    data = json.load(f)
                    
                    # 尝试不同的数据结构
                    if isinstance(data, list):
                        # 消息列表
                        for msg in data:
                            step = self._extract_step_from_message(msg, step_id + 1, log_file)
                            if step:
                                steps.append(step)
                                step_id += 1
                    elif isinstance(data, dict):
                        # 可能是 GroupChat 或其他结构
                        messages = data.get('messages', data.get('chat_history', []))
                        if isinstance(messages, list):
                            for msg in messages:
                                step = self._extract_step_from_message(msg, step_id + 1, log_file)
                                if step:
                                    steps.append(step)
                                    step_id += 1
                                
        except Exception as e:
            print(f"   ❌ 读取文件失败: {e}")
        
        return steps
    
    def _extract_step_from_message(self, message: Dict, step_id: int, source_file: Path) -> ExecutionStep:
        """从单条消息中提取执行步骤"""
        
        # 提取角色/发送者
        sender = message.get('name', message.get('role', message.get('sender', 'unknown')))
        
        # 提取内容
        content = message.get('content', message.get('message', ''))
        if isinstance(content, list):
            # 可能是多部分内容
            content = ' '.join([str(c) for c in content])
        
        if not content or not content.strip():
            return None
        
        # 确定步骤类型
        if sender.lower() in ['user', 'human']:
            step_type = "User Input"
        elif sender.lower() in ['assistant', 'agent', 'ai']:
            step_type = "Agent Thought"
        elif 'tool' in sender.lower() or 'function' in sender.lower():
            step_type = f"Tool Call: {sender}"
        else:
            step_type = f"Message: {sender}"
        
        # 提取元数据
        metadata = {
            'sender': sender,
            'source_file': source_file.name
        }
        
        # 提取额外信息
        if 'tool_calls' in message:
            metadata['tool_calls'] = message['tool_calls']
        if 'function_call' in message:
            metadata['function_call'] = message['function_call']
        
        # 提取时间戳
        timestamp = message.get('timestamp', message.get('time', message.get('created_at', 0)))
        
        return ExecutionStep(
            step_id=step_id,
            timestamp=timestamp,
            step_type=step_type,
            content=str(content)[:2000],  # 限制长度
            metadata=metadata
        )

    def analyze_metrics(self, steps: List[ExecutionStep]) -> Dict[str, Any]:
        """计算 AutoGen 特有的指标"""
        total_steps = len(steps)
        
        # 统计不同类型的消息
        user_inputs = sum(1 for s in steps if s.step_type == "User Input")
        agent_thoughts = sum(1 for s in steps if s.step_type == "Agent Thought")
        tool_calls = sum(1 for s in steps if "Tool Call" in s.step_type)
        
        # 统计参与的 Agent 数量
        unique_agents = set()
        for step in steps:
            if step.metadata and 'sender' in step.metadata:
                unique_agents.add(step.metadata['sender'])
        
        return {
            "framework": "AutoGen",
            "total_steps": total_steps,
            "user_inputs": user_inputs,
            "agent_thoughts": agent_thoughts,
            "tool_calls": tool_calls,
            "unique_agents": len(unique_agents),
            "agent_list": list(unique_agents),
            "is_multi_agent": len(unique_agents) > 1
        }
