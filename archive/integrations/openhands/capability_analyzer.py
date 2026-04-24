"""
OpenHands 能力分析器

分析 OpenHands 的能力边界、性能瓶颈和缺口
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class CapabilityAnalyzer:
    """
    OpenHands 能力分析器
    
    分析内容:
    - 支持的语言和框架
    - 可用工具列表
    - 执行成功率统计
    - 性能指标
    """
    
    def __init__(self, openhands_client):
        self.client = openhands_client
        self.capability_cache: Dict[str, Any] = {}
    
    async def analyze(self) -> Dict[str, Any]:
        """
        全面分析 OpenHands 能力
        
        Returns:
            {
                "supported_languages": [...],
                "available_tools": [...],
                "performance_metrics": {...},
                "capability_gaps": [...],
                "analyzed_at": "..."
            }
        """
        # 获取基本信息
        capabilities = await self._get_capabilities()
        
        # 分析性能
        performance = await self._analyze_performance()
        
        # 识别能力缺口
        gaps = await self._identify_gaps(capabilities, performance)
        
        result = {
            "supported_languages": capabilities.get("languages", []),
            "available_tools": capabilities.get("tools", []),
            "version": capabilities.get("version", "unknown"),
            "performance_metrics": performance,
            "capability_gaps": gaps,
            "strengths": self._identify_strengths(capabilities, performance),
            "weaknesses": self._identify_weaknesses(gaps, performance),
            "analyzed_at": datetime.now().isoformat()
        }
        
        # 缓存结果
        self.capability_cache = result
        
        return result
    
    async def _get_capabilities(self) -> Dict[str, Any]:
        """获取 OpenHands 能力信息"""
        try:
            # 尝试从 API 获取
            if hasattr(self.client, 'get_capabilities'):
                return await self.client.get_capabilities()
            
            # 默认能力（如果 API 不可用）
            return {
                "languages": ["python", "javascript", "typescript", "java", "go"],
                "tools": ["file_read", "file_write", "code_execute", "bash"],
                "version": "unknown"
            }
        except Exception as e:
            print(f"⚠️ Failed to get capabilities: {e}")
            return {
                "languages": [],
                "tools": [],
                "version": "unknown",
                "error": str(e)
            }
    
    async def _analyze_performance(self) -> Dict[str, Any]:
        """分析性能指标"""
        try:
            # 从历史执行记录中分析
            history = self.client.get_history() if hasattr(self.client, 'get_history') else []
            
            if not history:
                return {
                    "total_tasks": 0,
                    "success_rate": 0,
                    "avg_duration": 0,
                    "avg_tokens": 0
                }
            
            total = len(history)
            success_count = sum(1 for h in history if h.get("result", {}).get("success", False))
            
            durations = [h.get("result", {}).get("duration", 0) for h in history]
            tokens = [h.get("result", {}).get("tokens_used", 0) for h in history]
            
            return {
                "total_tasks": total,
                "success_count": success_count,
                "fail_count": total - success_count,
                "success_rate": success_count / max(total, 1),
                "avg_duration": sum(durations) / max(len(durations), 1),
                "avg_tokens": sum(tokens) / max(len(tokens), 1),
                "p95_duration": sorted(durations)[int(len(durations) * 0.95)] if durations else 0
            }
        except Exception as e:
            print(f"⚠️ Failed to analyze performance: {e}")
            return {
                "total_tasks": 0,
                "success_rate": 0,
                "avg_duration": 0,
                "avg_tokens": 0,
                "error": str(e)
            }
    
    async def _identify_gaps(
        self,
        capabilities: Dict,
        performance: Dict
    ) -> List[Dict[str, Any]]:
        """识别能力缺口"""
        gaps = []
        
        # 检查成功率
        if performance.get("success_rate", 1) < 0.8:
            gaps.append({
                "type": "low_success_rate",
                "severity": "high",
                "current_value": performance.get("success_rate", 0),
                "target_value": 0.8,
                "description": f"Success rate is {performance.get('success_rate', 0)*100:.1f}%, target is 80%"
            })
        
        # 检查耗时
        if performance.get("avg_duration", 0) > 60:
            gaps.append({
                "type": "slow_execution",
                "severity": "medium",
                "current_value": performance.get("avg_duration", 0),
                "target_value": 60,
                "description": f"Average duration is {performance.get('avg_duration', 0):.1f}s, target is <60s"
            })
        
        # 检查语言支持（示例：如果没有 TypeScript）
        supported_languages = capabilities.get("languages", [])
        if "typescript" not in [lang.lower() for lang in supported_languages]:
            gaps.append({
                "type": "missing_language_support",
                "severity": "medium",
                "language": "typescript",
                "description": "TypeScript support is missing"
            })
        
        return gaps
    
    def _identify_strengths(
        self,
        capabilities: Dict,
        performance: Dict
    ) -> List[str]:
        """识别优势"""
        strengths = []
        
        # 高成功率
        if performance.get("success_rate", 0) >= 0.9:
            strengths.append(f"High success rate: {performance['success_rate']*100:.1f}%")
        
        # 多语言支持
        languages = capabilities.get("languages", [])
        if len(languages) >= 5:
            strengths.append(f"Supports {len(languages)} programming languages")
        
        # 丰富的工具集
        tools = capabilities.get("tools", [])
        if len(tools) >= 10:
            strengths.append(f"Rich toolset with {len(tools)} tools")
        
        return strengths
    
    def _identify_weaknesses(
        self,
        gaps: List[Dict],
        performance: Dict
    ) -> List[str]:
        """识别弱点"""
        weaknesses = []
        
        for gap in gaps:
            if gap.get("severity") == "high":
                weaknesses.append(gap["description"])
        
        # 低成功率
        if performance.get("success_rate", 1) < 0.7:
            weaknesses.append("Low success rate needs improvement")
        
        return weaknesses
    
    def get_cached_result(self) -> Optional[Dict]:
        """获取缓存的分析结果"""
        return self.capability_cache if self.capability_cache else None
