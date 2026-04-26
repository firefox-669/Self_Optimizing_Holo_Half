"""
OpenSpace 框架专用的链路采集与分析插件
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from .base import BaseAnalyzer, ExecutionStep


class OpenSpaceAnalyzer(BaseAnalyzer):
    @property
    def name(self) -> str:
        return "openspace_analyzer"

    def is_compatible(self, source_path: str) -> bool:
        """判断该插件是否能处理指定路径的数据源"""
        path = Path(source_path)
        # 如果是目录，检查里面是否有 traj.jsonl 或 conversations.jsonl
        if path.is_dir():
            return any(f.name in ['traj.jsonl', 'conversations.jsonl'] for f in path.rglob('*.jsonl'))
        # 如果是文件，检查是否是 jsonl
        return path.suffix.lower() in ['.json', '.jsonl']

    def collect_trace(self, source_path: str) -> List[ExecutionStep]:
        steps = []
        path = Path(source_path)
            
        # 确定要处理的目录
        if path.is_file():
            search_dir = path.parent
        else:
            search_dir = path
                
        # 寻找目录下所有的 .jsonl 文件
        jsonl_files = list(search_dir.rglob('*.jsonl'))
        # 按修改时间倒序排列，优先处理最新的
        jsonl_files = sorted(jsonl_files, key=lambda x: x.stat().st_mtime, reverse=True)
        print(f"🔍 在 {search_dir} 下找到 {len(jsonl_files)} 个 .jsonl 文件")
            
        global_step_id = 0  # 使用全局计数器
        
        # 【核心修复】尝试从 metadata.json 中提取任务描述作为 Step 1
        meta_file = search_dir / 'metadata.json'
        if meta_file.exists():
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    task_desc = meta.get('task', meta.get('instruction', ''))
                    if task_desc:
                        global_step_id += 1
                        steps.append(ExecutionStep(
                            step_id=global_step_id,
                            timestamp=meta.get('start_time', 0),
                            step_type="User Instruction",
                            content=task_desc,
                            metadata={'source_file': 'metadata.json'}
                        ))
                        print(f"   ✅ 已提取任务指令: {task_desc[:50]}...")
            except:
                pass

        for jf in jsonl_files:
            # 跳过太小的文件（可能是空的或只有元数据）
            if jf.stat().st_size < 100:
                continue
                
            try:
                with open(jf, 'r', encoding='utf-8') as f:
                    local_count = 0
                    lines = f.readlines()
                    
                    # 预检查：如果第一行包含 'traj' 或 'agent_actions' 特征，则重点解析
                    is_traj = 'traj' in jf.name or 'agent_actions' in jf.name
                    
                    for line in lines:
                        if not line.strip():
                            continue
                        try:
                            event = json.loads(line)
                        except:
                            continue
                        
                        extracted = False
                        
                        # 尝试格式 A: 平铺式 (traj.jsonl 常见)
                        if 'role' in event and 'content' in event:
                            content = str(event.get('content', ''))
                            # 过滤掉无意义的错误信息
                            if '[ERROR] unknown error' in content or not content.strip():
                                continue
                                
                            global_step_id += 1
                            role = event['role']
                            step_type = "Agent Thought" if role == 'assistant' else ("User Input" if role == 'user' else "Tool Response")
                            steps.append(ExecutionStep(
                                step_id=global_step_id,
                                timestamp=event.get('timestamp', 0),
                                step_type=step_type,
                                content=content[:2000] + "..." if len(content) > 2000 else content,
                                metadata={'source_file': str(jf.name)}
                            ))
                            local_count += 1
                            extracted = True
                        
                        # 尝试格式 B: 嵌套式 (conversations.jsonl 常见)
                        if not extracted and event.get('type') == 'iteration':
                            delta_msgs = event.get('delta_messages', [])
                            for msg in delta_msgs:
                                role = msg.get('role', 'unknown')
                                content = str(msg.get('content', ''))
                                
                                # 提取工具调用信息 (如果有)
                                tool_calls = msg.get('tool_calls', [])
                                if tool_calls:
                                    for tc in tool_calls:
                                        global_step_id += 1
                                        func_name = tc.get('function', {}).get('name', 'unknown_tool')
                                        args = tc.get('function', {}).get('arguments', '{}')
                                        step_content = f"调用工具: {func_name}\n参数: {args}"
                                        steps.append(ExecutionStep(
                                            step_id=global_step_id,
                                            timestamp=event.get('timestamp', 0),
                                            step_type=f"Tool Call: {func_name}",
                                            content=step_content[:2000],
                                            metadata={'source_file': str(jf.name)}
                                        ))
                                        local_count += 1
                                
                                # 处理普通文本内容（不再过滤错误信息，保留完整的反馈闭环）
                                if content.strip():
                                    global_step_id += 1
                                    step_type = "Agent Thought" if role == 'assistant' else ("User Input" if role == 'user' else "Tool Response")
                                    steps.append(ExecutionStep(
                                        step_id=global_step_id,
                                        timestamp=event.get('timestamp', 0),
                                        step_type=step_type,
                                        content=content[:2000] + "..." if len(content) > 2000 else content,
                                        metadata={'source_file': str(jf.name)}
                                    ))
                                    local_count += 1
                            extracted = True

                        # 尝试格式 C: agent_actions.jsonl (可能有 action 字段)
                        if not extracted and 'action' in event:
                            global_step_id += 1
                            action = event.get('action', 'unknown')
                            steps.append(ExecutionStep(
                                step_id=global_step_id,
                                timestamp=event.get('timestamp', 0),
                                step_type=f"Action: {action}",
                                content=str(event)[:300],
                                metadata={'source_file': str(jf.name)}
                            ))
                            local_count += 1
                            extracted = True

                    if local_count > 0:
                        print(f"   ✅ 成功解析 {jf.name}: 提取 {local_count} 步")
            except Exception as e:
                print(f"⚠️  解析 {jf} 失败: {e}")
                    
        # 【核心修复】按时间戳严格排序，确保逻辑闭环
        steps.sort(key=lambda x: x.timestamp)
        
        # 重新分配连续的 Step ID
        for i, step in enumerate(steps):
            step.step_id = i + 1
            
        return steps

    def analyze_metrics(self, steps: List[ExecutionStep]) -> Dict[str, Any]:
        """计算 OpenSpace 特有的指标"""
        total_steps = len(steps)
        tool_calls = sum(1 for s in steps if s.step_type == 'tool_call')
        
        # 简单的记忆效率估算：如果内容长度极长但步骤很少，可能效率低
        total_content_len = sum(len(s.content) for s in steps)
        
        return {
            "framework": "OpenSpace",
            "total_steps": total_steps,
            "tool_call_count": tool_calls,
            "avg_content_length": total_content_len / max(1, total_steps),
            "is_long_chain": total_steps > 20
        }
