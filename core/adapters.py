from abc import ABC, abstractmethod
from typing import List, Dict, Any
from core.sohh_protocol import SOHHEvent

class BaseAdapter(ABC):
    """所有框架适配器的基类"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.events: List[SOHHEvent] = []

    @abstractmethod
    def intercept_action(self, action: Any) -> SOHHEvent:
        """拦截动作并转换为标准事件"""
        pass

    @abstractmethod
    def intercept_observation(self, observation: Any, event: SOHHEvent) -> SOHHEvent:
        """拦截观察结果并更新事件状态"""
        pass

    def get_history(self) -> List[Dict]:
        return [e.to_dict() for e in self.events]

    def clear_history(self):
        self.events.clear()

class OpenHandsAdapter(BaseAdapter):
    """OpenHands 框架的专用适配器"""
    
    def __init__(self):
        super().__init__("openhands")

    def intercept_action(self, action: Any) -> SOHHEvent:
        # 这里需要根据 OpenHands 的实际 Action 对象进行映射
        # 示例逻辑：
        event = SOHHEvent(
            agent_name=self.agent_name,
            action_type=action.action if hasattr(action, 'action') else 'unknown',
            action_payload={"content": str(action)}
        )
        self.events.append(event)
        return event

    def intercept_observation(self, observation: Any, event: SOHHEvent) -> SOHHEvent:
        # 更新事件的结果和性能指标
        event.status = "success" if not getattr(observation, 'error', None) else "error"
        event.observation = str(observation)[:500]  # 截取前500字符防止过长
        return event
