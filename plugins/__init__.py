"""
SOHH 插件系统

支持多种 Agent 框架的日志解析和数据采集
"""

from .base import BaseAnalyzer, ExecutionStep
from .openspace_analyzer import OpenSpaceAnalyzer
from .openhands_analyzer import OpenHandsAnalyzer

# 注册所有可用的分析器
AVAILABLE_ANALYZERS = [
    OpenSpaceAnalyzer(),
    OpenHandsAnalyzer(),
]


def get_analyzer_for_source(source_path: str):
    """
    根据数据源路径自动选择合适的分析器
    
    Args:
        source_path: 数据源路径（文件或目录）
        
    Returns:
        兼容的分析器实例，如果没有则返回 None
    """
    for analyzer in AVAILABLE_ANALYZERS:
        if analyzer.is_compatible(source_path):
            return analyzer
    return None


__all__ = [
    'BaseAnalyzer',
    'ExecutionStep', 
    'OpenSpaceAnalyzer',
    'OpenHandsAnalyzer',
    'AVAILABLE_ANALYZERS',
    'get_analyzer_for_source'
]