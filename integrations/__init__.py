"""
集成模块
提供 OpenHands 和 OpenSpace 的真实 MCP 集成
"""

from .base import MCPIntegration, OpenHandsIntegration, OpenSpaceIntegration

__all__ = [
    "MCPIntegration",
    "OpenHandsIntegration", 
    "OpenSpaceIntegration",
]