from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import time
import uuid

@dataclass
class SOHHEvent:
    """SOHH 标准化评估事件"""
    event_id: str = ""
    timestamp: float = 0.0
    agent_name: str = ""
    
    # 动作信息
    action_type: str = ""  # e.g., 'read_file', 'write_file', 'run_command', 'think'
    action_payload: Dict[str, Any] = None
    
    # 结果信息
    status: str = "pending"  # 'success', 'error', 'pending'
    observation: str = ""
    error_message: str = ""
    
    # 性能指标
    duration_ms: float = 0.0
    tokens_used: int = 0
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = time.time()
        if self.action_payload is None:
            self.action_payload = {}

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'SOHHEvent':
        return cls(**data)
