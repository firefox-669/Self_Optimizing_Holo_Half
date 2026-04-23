"""
OpenSpace 能力分析器
分析 OpenSpace 的自我进化能力和 Skills
"""

import asyncio
from typing import Any, Dict, List
from datetime import datetime


class OpenSpaceAnalyzer:
    """
    OpenSpace 能力分析器
    分析 OpenSpace 的进化能力并生成改进建议
    """
    
    def __init__(self, client=None):
        self.client = client
        self._analysis_cache: Dict[str, Any] = {}
        self._last_analysis = None
    
    async def analyze(self) -> Dict[str, Any]:
        """全面分析 OpenSpace 能力"""
        
        # 检查连接状态
        connected = False
        if self.client:
            connected = self.client.is_connected() if hasattr(self.client, 'is_connected') else False
        
        # 获取 Skills
        skills = []
        evolution_history = []
        quality_metrics = {}
        
        if connected and self.client:
            try:
                skills = self.client.get_skills() if hasattr(self.client, 'get_skills') else []
            except:
                pass
            
            try:
                evolution_history = self.client.get_evolution_history() if hasattr(self.client, 'get_evolution_history') else []
            except:
                pass
            
            try:
                quality_metrics = self.client.get_quality_metrics() if hasattr(self.client, 'get_quality_metrics') else {}
            except:
                pass
        
        analysis = {
            "connected": connected,
            "timestamp": datetime.now().isoformat(),
            "skills": skills,
            "skills_count": len(skills),
            "evolution_capabilities": self._analyze_evolution_capabilities(skills),
            "quality_metrics": quality_metrics,
            "evolution_history": evolution_history,
            "mcp_tools": await self._get_mcp_tools(),
        }
        
        self._analysis_cache = analysis
        self._last_analysis = datetime.now()
        
        return analysis
    
    def _analyze_evolution_capabilities(self, skills: List[Dict]) -> Dict[str, Any]:
        """分析进化能力"""
        
        # 检测可用的进化模式
        evolution_modes = {
            "auto_fix": True,
            "auto_improve": True,
            "auto_learn": True,
            "derived": True,
            "captured": True,
        }
        
        # 分析 Skills 质量
        skill_quality = {
            "total_skills": len(skills),
            "high_quality_skills": sum(1 for s in skills if s.get("quality_score", 0) > 0.8),
            "avg_quality": sum(s.get("quality_score", 0) for s in skills) / max(len(skills), 1) if skills else 0,
        }
        
        return {
            "supported_modes": evolution_modes,
            "skill_quality": skill_quality,
            "can_self_evolve": len(skills) > 0,
            "can_share_skills": True,
            "supports_cloud": self._check_cloud_support(),
        }
    
    def _check_cloud_support(self) -> bool:
        """检查云端支持"""
        if self.client:
            return getattr(self.client, 'cloud_enabled', False)
        return False
    
    async def _get_mcp_tools(self) -> List[Dict]:
        """获取 MCP 工具"""
        if not self.client:
            return []
        
        tools = [
            {"name": "delegate-task", "description": "执行任务并自动进化"},
            {"name": "skill-discovery", "description": "搜索 Skills"},
            {"name": "evolve-skill", "description": "进化指定 Skill"},
        ]
        
        return tools
    
    def get_cached_analysis(self) -> Dict[str, Any]:
        """获取缓存的分析结果"""
        return self._analysis_cache
    
    def get_change_recommendations(self) -> List[Dict]:
        """生成改进建议"""
        recommendations = []
        
        if not self._analysis_cache.get("connected"):
            recommendations.append({
                "type": "enhance_openspace",
                "priority": 10,
                "title": "改进 OpenSpace 连接",
                "description": "OpenSpace 未连接，需要安装或启动服务",
                "implementation": "安装 OpenSpace: pip install -e git+https://github.com/HKUDS/OpenSpace.git",
            })
        
        # 基于 Skills 生成建议
        skills_count = self._analysis_cache.get("skills_count", 0)
        if skills_count < 5:
            recommendations.append({
                "type": "enhance_openspace",
                "priority": 7,
                "title": "增加 Skills",
                "description": f"当前仅有 {skills_count} 个 Skills，建议获取更多",
                "implementation": "通过执行任务自动捕获 Skills",
            })
        
        # 基于进化历史生成建议
        evolution_history = self._analysis_cache.get("evolution_history", [])
        if len(evolution_history) < 3:
            recommendations.append({
                "type": "enhance_openspace",
                "priority": 6,
                "title": "增加进化次数",
                "description": f"仅有 {len(evolution_history)} 次进化，建议更频繁使用",
                "implementation": "多执行任务触发自动进化",
            })
        
        return recommendations