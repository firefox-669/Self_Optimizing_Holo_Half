"""
SOHH 插件系统核心接口
定义了所有分析插件必须遵循的标准契约。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExecutionStep:
    """标准化的执行步骤数据模型"""
    step_id: int
    timestamp: float
    step_type: str  # e.g., 'thought', 'action', 'observation', 'tool_call'
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAnalyzer(ABC):
    """所有分析插件的基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称，用于日志和配置"""
        pass

    @abstractmethod
    def is_compatible(self, source_path: str) -> bool:
        """判断该插件是否能处理指定路径的数据源"""
        pass

    @abstractmethod
    def collect_trace(self, source_path: str) -> List[ExecutionStep]:
        """从数据源采集原始执行链路"""
        pass

    @abstractmethod
    def analyze_metrics(self, steps: List[ExecutionStep]) -> Dict[str, Any]:
        """基于采集到的链路计算评估指标（如记忆效率、复杂度等）"""
        pass
