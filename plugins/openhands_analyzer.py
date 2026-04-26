"""
OpenHands 框架专用的链路采集与分析插件

此插件通过解析 OpenHands 生成的会话目录来提取执行链路，无需修改 OpenHands 任何代码。

OpenHands 日志结构:
- sessions/{session_id}/events/{event_id}.json - 每个事件单独存储
- sessions/{session_id}/metadata.json - 会话元数据
- sessions/{session_id}/init.json - 初始化数据
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from .base import BaseAnalyzer, ExecutionStep


class OpenHandsAnalyzer(BaseAnalyzer):
    """OpenHands 日志分析器"""
    
    @property
    def name(self) -> str:
        return "openhands_analyzer"

    def is_compatible(self, source_path: str) -> bool:
        """判断该插件是否能处理指定路径的数据源"""
        path = Path(source_path)
        
        # 检查是否是 OpenHands 会话目录
        if path.is_dir():
            # 检查是否有 events 子目录或 metadata.json
            has_events = (path / 'events').exists()
            has_metadata = (path / 'metadata.json').exists()
            return has_events or has_metadata
        
        return False

    def collect_trace(self, source_path: str) -> List[ExecutionStep]:
        """
        从 OpenHands 会话目录中收集执行链路
        
        Args:
            source_path: 会话目录路径 (例如: sessions/abc123/)
            
        Returns:
            执行步骤列表
        """
        steps = []
        path = Path(source_path)
        
        if not path.is_dir():
            print(f"⚠️  {source_path} 不是目录")
            return steps
        
        global_step_id = 0
        
        # 1. 尝试从 metadata.json 中提取任务描述
        meta_file = path / 'metadata.json'
        task_description = ""
        if meta_file.exists():
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    task_description = meta.get('task', meta.get('initial_user_msg', ''))
                    if task_description:
                        global_step_id += 1
                        steps.append(ExecutionStep(
                            step_id=global_step_id,
                            timestamp=meta.get('created_at', 0),
                            step_type="User Instruction",
                            content=task_description[:500],
                            metadata={'source': 'metadata.json'}
                        ))
                        print(f"   ✅ 已提取任务指令: {task_description[:50]}...")
            except Exception as e:
                print(f"   ⚠️  读取 metadata.json 失败: {e}")
        
        # 2. 解析 events 目录中的所有事件文件
        events_dir = path / 'events'
        if not events_dir.exists():
            print(f"   ⚠️  events 目录不存在: {events_dir}")
            return steps
        
        # 获取所有 JSON 文件并按ID排序
        event_files = sorted(
            [f for f in events_dir.glob('*.json') if f.stem.isdigit()],
            key=lambda x: int(x.stem)
        )
        
        print(f"🔍 在 {events_dir} 下找到 {len(event_files)} 个事件文件")
        
        for event_file in event_files:
            try:
                with open(event_file, 'r', encoding='utf-8') as f:
                    event_data = json.load(f)
                
                # 提取事件类型和内容
                event_type = event_data.get('type', 'unknown')
                source = event_data.get('source', 'unknown')
                
                # 根据事件类型确定 step_type
                if source == 'user':
                    step_type = "User Input"
                elif source == 'agent':
                    step_type = "Agent Thought"
                elif 'action' in event_type.lower():
                    step_type = f"Action: {event_type}"
                elif 'observation' in event_type.lower():
                    step_type = f"Observation: {event_type}"
                else:
                    step_type = event_type
                
                # 提取内容
                content = self._extract_content(event_data)
                
                if content.strip():  # 只添加有内容的步骤
                    global_step_id += 1
                    steps.append(ExecutionStep(
                        step_id=global_step_id,
                        timestamp=event_data.get('timestamp', 0) or event_data.get('created_at', 0),
                        step_type=step_type,
                        content=content[:2000] + "..." if len(content) > 2000 else content,
                        metadata={
                            'event_id': event_file.stem,
                            'event_type': event_type,
                            'source': source
                        }
                    ))
                    
            except Exception as e:
                print(f"   ⚠️  解析 {event_file.name} 失败: {e}")
        
        # 按时间戳排序
        steps.sort(key=lambda x: x.timestamp if x.timestamp else 0)
        
        # 重新分配连续的 Step ID
        for i, step in enumerate(steps):
            step.step_id = i + 1
        
        print(f"   ✅ 成功解析: 提取 {len(steps)} 步")
        
        return steps
    
    def _extract_content(self, event_data: Dict) -> str:
        """从事件数据中提取可读内容"""
        
        # 尝试多种可能的内容字段
        content_fields = [
            'content',
            'message',
            'text',
            'thought',
            'command',
            'output',
            'response'
        ]
        
        for field in content_fields:
            if field in event_data:
                value = event_data[field]
                if isinstance(value, str):
                    return value
                elif isinstance(value, dict):
                    return json.dumps(value, ensure_ascii=False)[:500]
        
        # 如果没有找到标准字段，返回整个事件的简要表示
        return json.dumps(event_data, ensure_ascii=False)[:300]

    def analyze_metrics(self, steps: List[ExecutionStep]) -> Dict[str, Any]:
        """计算 OpenHands 特有的指标"""
        total_steps = len(steps)
        
        # 统计不同类型的事件
        user_inputs = sum(1 for s in steps if s.step_type == "User Input")
        agent_thoughts = sum(1 for s in steps if s.step_type == "Agent Thought")
        actions = sum(1 for s in steps if "Action" in s.step_type)
        observations = sum(1 for s in steps if "Observation" in s.step_type)
        
        return {
            "framework": "OpenHands",
            "total_steps": total_steps,
            "user_inputs": user_inputs,
            "agent_thoughts": agent_thoughts,
            "actions": actions,
            "observations": observations,
            "is_long_chain": total_steps > 20
        }
