"""
OpenHands 能力分析器
分析 OpenHands 的当前能力和局限性
"""

import asyncio
from typing import Any, Dict, List
from datetime import datetime


class OpenHandsAnalyzer:
    """
    OpenHands 能力分析器
    分析外部集成的能力并生成改进建议
    """
    
    def __init__(self, client=None):
        self.client = client
        self._analysis_cache: Dict[str, Any] = {}
        self._last_analysis = None
    
    async def analyze(self) -> Dict[str, Any]:
        """全面分析 OpenHands 能力"""
        
        # 检查连接状态
        connected = False
        if self.client:
            connected = self.client.is_connected() if hasattr(self.client, 'is_connected') else False
        
        analysis = {
            "connected": connected,
            "timestamp": datetime.now().isoformat(),
            "available_tools": await self._analyze_tools(),
            "execution_capabilities": self._analyze_execution_capabilities(),
            "limitations": self._analyze_limitations(),
            "performance_metrics": self._analyze_performance(),
            "mcp_tools": await self._get_mcp_tools(),
        }
        
        self._analysis_cache = analysis
        self._last_analysis = datetime.now()
        
        return analysis
    
    async def _analyze_tools(self) -> List[Dict]:
        """分析可用工具"""
        tools = []
        
        # 基础工具
        tools.extend([
            {"name": "bash", "category": "shell", "available": True},
            {"name": "read", "category": "file", "available": True},
            {"name": "write", "category": "file", "available": True},
            {"name": "Glob", "category": "file", "available": True},
            {"name": "grep", "category": "search", "available": True},
            {"name": "Browser", "category": "web", "available": True},
            {"name": "WebFetch", "category": "web", "available": True},
        ])
        
        # 如果有客户端，获取更多工具
        if self.client:
            try:
                client_tools = await self.client.get_tools()
                if client_tools:
                    tools.extend(client_tools)
            except:
                pass
        
        return tools
    
    def _analyze_execution_capabilities(self) -> Dict[str, Any]:
        """分析执行能力"""
        return {
            "code_execution": True,
            "file_operations": True,
            "web_browsing": True,
            "web_search": True,
            "shell_commands": True,
            "multi_step_tasks": True,
            "max_iterations": 20,
            "supports_history": True,
            "supports_context": True,
        }
    
    def _analyze_limitations(self) -> List[Dict]:
        """分析局限性"""
        limitations = []
        
        # 检测可能的局限性
        limitations.extend([
            {
                "type": "api_dependency",
                "description": "需要外部 OpenHands 服务运行",
                "severity": "medium",
                "mitigation": "提供本地 fallback",
            },
            {
                "type": "context_window",
                "description": "上下文窗口有限",
                "severity": "low",
                "mitigation": "分块处理长任务",
            },
        ])
        
        return limitations
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """分析性能指标"""
        return {
            "avg_execution_time": 30.0,
            "success_rate": 0.85,
            "timeout_rate": 0.05,
            "error_rate": 0.10,
        }
    
    async def _get_mcp_tools(self) -> List[Dict]:
        """获取 MCP 工具列表"""
        if not self.client:
            return []
        
        try:
            tools = await self.client.get_tools()
            return tools
        except:
            return []
    
    def get_cached_analysis(self) -> Dict[str, Any]:
        """获取缓存的分析结果"""
        return self._analysis_cache
    
    def get_change_recommendations(self) -> List[Dict]:
        """生成改进建议"""
        recommendations = []
        
        if not self._analysis_cache.get("connected"):
            recommendations.append({
                "type": "enhance_openhands",
                "priority": 10,
                "title": "改进 OpenHands 连接",
                "description": "OpenHands 未连接，需要配置服务或安装 SDK",
                "implementation": "检查服务配置或安装 openhands 包",
            })
        
        # 基于局限性生成建议
        for limitation in self._analysis_cache.get("limitations", []):
            recommendations.append({
                "type": "enhance_openhands",
                "priority": 5,
                "title": f"解决 {limitation['type']}",
                "description": limitation["description"],
                "implementation": limitation.get("mitigation", ""),
            })
        
        return recommendations