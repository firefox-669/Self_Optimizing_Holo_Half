"""
OpenSpace 集成模块
通过 MCP 与 OpenSpace 服务通信，实现自我进化
"""

from .client import OpenSpaceClient
from .skill_analyzer import SkillAnalyzer

__all__ = [
    "OpenSpaceClient",
    "SkillAnalyzer"
]