"""
Self_Optimizing_Holo_Half - 自进化智能编程系统
真实集成 OpenHands + OpenSpace + 插件化扩展架构
"""

from Self_Optimizing_Holo_Half.core.engine import SelfOptimizingEngine
from Self_Optimizing_Holo_Half.core.evolution_loop import SelfEvolutionLoop
from Self_Optimizing_Holo_Half.executor.executor import OpenHandsExecutor
from Self_Optimizing_Holo_Half.evolution.evolver import EvoEngine
from Self_Optimizing_Holo_Half.monitor.safety import SafetyMonitor
from Self_Optimizing_Holo_Half.patches.fixes import PatchManager
from Self_Optimizing_Holo_Half.ai_news.integrator import NewsIntegrator

from Self_Optimizing_Holo_Half.integrations.openhands import OpenHandsClient
from Self_Optimizing_Holo_Half.integrations.openspace import OpenSpaceClient
from Self_Optimizing_Holo_Half.analyzer import (
    OpenHandsAnalyzer,
    OpenSpaceAnalyzer,
    ProjectSelfAnalyzer,
    InfoCollector,
)
from Self_Optimizing_Holo_Half.evolution import EvolutionSuggestionEngine
from Self_Optimizing_Holo_Half.version_control import (
    SnapshotManager,
    ChangeLogger,
    RollbackManager,
)
from Self_Optimizing_Holo_Half.optimizer import AutoOptimizer, EffectEvaluator
from Self_Optimizing_Holo_Half.reporting import DailyReportGenerator, DeepAnalyzer

__version__ = "2.0.0"
__all__ = [
    # 核心引擎
    "SelfOptimizingEngine",
    "SelfEvolutionLoop",
    
    # 原有组件
    "OpenHandsExecutor",
    "EvoEngine",
    "SafetyMonitor",
    "PatchManager",
    "NewsIntegrator",
    
    # 新集成
    "OpenHandsClient",
    "OpenSpaceClient",
    
    # 分析器
    "OpenHandsAnalyzer",
    "OpenSpaceAnalyzer",
    "ProjectSelfAnalyzer",
    "InfoCollector",
    
    # 建议
    "EvolutionSuggestionEngine",
    
    # 版本控制
    "SnapshotManager",
    "ChangeLogger",
    "RollbackManager",
    
    # 优化器
    "AutoOptimizer",
    "EffectEvaluator",
    
    # 报告
    "DailyReportGenerator",
    "DeepAnalyzer",
]