"""
核心模块
提供主引擎和自我进化循环
"""

from .engine import SelfOptimizingEngine
from .evolution_loop import SelfEvolutionLoop

__all__ = ["SelfOptimizingEngine", "SelfEvolutionLoop"]