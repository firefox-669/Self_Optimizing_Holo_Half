"""
Evolution Suggestion 引擎
生成和管理 Evolution Suggestions
使用 LLM 进行智能分析
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class EvolutionSuggestionEngine:
    """
    Evolution Suggestion 引擎
    综合分析结果生成可执行的优化建议
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self._suggestions: List[Dict] = []
        self._history: List[Dict] = []
        self._load_history()
    
    def _load_history(self):
        """加载历史建议"""
        history_file = self.workspace / ".sohh_cache" / "suggestion_history.json"
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._history = data.get("history", [])
    
    def _save_history(self):
        """保存历史建议"""
        history_file = self.workspace / ".sohh_cache" / "suggestion_history.json"
        history_file.parent.mkdir(exist_ok=True)
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump({
                "history": self._history,
                "updated": datetime.now().isoformat(),
            }, f, indent=2)
    
    async def generate_suggestions(
        self,
        existing_analysis: Dict[str, Any] = None,
        info_analysis: List[Dict] = None,
        project_analysis: Dict[str, Any] = None,
        use_llm: bool = True,
    ) -> List[Dict]:
        """
        生成 Evolution Suggestions
        
        综合所有分析结果，生成可执行的建议
        
        Args:
            existing_analysis: 现有能力分析
            info_analysis: 资讯分析结果
            project_analysis: 项目自分析结果
            use_llm: 是否使用 LLM 分析（默认 True）
        """
        suggestions = []
        llm_suggestions = []
        
        # 1. 基于现有能力分析的建议（规则引擎）
        if existing_analysis:
            suggestions.extend(self._from_existing_analysis(existing_analysis))
        
        # 2. 基于资讯的建议（使用 LLM）
        if info_analysis and use_llm:
            try:
                logger.info("🧠 Using LLM to analyze info...")
                llm_suggestions = await self._analyze_with_llm(info_analysis)
                logger.info(f"✅ LLM generated {len(llm_suggestions)} suggestions")
            except Exception as e:
                logger.warning(f"⚠️ LLM analysis failed, falling back to rule-based: {e}")
                # Fallback: 使用规则引擎
                suggestions.extend(self._from_info_analysis(info_analysis))
        elif info_analysis:
            # 不使用 LLM，使用规则引擎
            suggestions.extend(self._from_info_analysis(info_analysis))
        
        # 3. 基于项目自分析的建议（规则引擎）
        if project_analysis:
            suggestions.extend(self._from_project_analysis(project_analysis))
        
        # 合并 LLM 建议和规则建议
        if llm_suggestions:
            suggestions.extend(llm_suggestions)
        
        # 去重并排序
        suggestions = self._deduplicate(suggestions)
        suggestions = self._prioritize(suggestions)
        
        self._suggestions = suggestions
        return suggestions
    
    def _from_existing_analysis(self, analysis: Dict[str, Any]) -> List[Dict]:
        """从现有能力分析生成建议"""
        suggestions = []
        
        # OpenHands 能力分析
        if "openhands" in analysis:
            oh_analysis = analysis.get("openhands", {})
            
            if not oh_analysis.get("connected"):
                suggestions.append({
                    "id": f"oh_connect_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "target": "openhands",
                    "type": "connection",
                    "title": "连接 OpenHands 服务",
                    "description": "OpenHands 未连接，需要配置服务或安装 SDK",
                    "implementation": "pip install openhands 或启动 Docker 服务",
                    "priority": 10,
                    "status": "pending",
                })
            
            for limit in oh_analysis.get("limitations", []):
                if limit.get("severity") == "high":
                    suggestions.append({
                        "id": f"oh_limit_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "target": "openhands",
                        "type": "limitation_fix",
                        "title": f"解决 {limit.get('type')}",
                        "description": limit.get("description", ""),
                        "implementation": limit.get("mitigation", ""),
                        "priority": 7,
                        "status": "pending",
                    })
        
        # OpenSpace 能力分析
        if "openspace" in analysis:
            os_analysis = analysis.get("openspace", {})
            
            if not os_analysis.get("connected"):
                suggestions.append({
                    "id": f"os_connect_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "target": "openspace",
                    "type": "connection",
                    "title": "连接 OpenSpace 服务",
                    "description": "OpenSpace 未连接，需要安装",
                    "implementation": "pip install -e git+https://github.com/HKUDS/OpenSpace.git",
                    "priority": 10,
                    "status": "pending",
                })
            
            skills_count = os_analysis.get("skills_count", 0)
            if skills_count < 5:
                suggestions.append({
                    "id": f"os_skills_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "target": "openspace",
                    "type": "skill_capture",
                    "title": "增加 Skills 数量",
                    "description": f"当前仅有 {skills_count} 个 Skills",
                    "implementation": "通过执行任务自动捕获 Skills",
                    "priority": 6,
                    "status": "pending",
                })
        
        return suggestions
    
    async def _analyze_with_llm(self, info_items: List[Dict]) -> List[Dict]:
        """
        使用 LLM 分析资讯，生成改进建议
        
        Args:
            info_items: 资讯列表
            
        Returns:
            LLM 生成的建议列表
        """
        from core.llm_client import LLMClient
        
        try:
            # 初始化 LLM 客户端
            llm = LLMClient()
            
            # 调用 LLM 分析
            suggestions = await llm.analyze_info(info_items)
            
            # 为每个建议添加 ID 和状态
            for i, suggestion in enumerate(suggestions):
                suggestion['id'] = f"llm_{suggestion.get('target', 'unknown')}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}"
                suggestion['status'] = 'pending'
                suggestion['generated_by'] = 'llm'
                suggestion['llm_provider'] = llm.provider
                suggestion['llm_model'] = llm.model
            
            return suggestions
        
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            raise
    
    def _from_info_analysis(self, info: List[Dict]) -> List[Dict]:
        """从资讯分析生成建议"""
        suggestions = []
        
        for item in info:
            target = item.get("target", "")
            title = item.get("improvement", "")
            priority = item.get("priority", 0.5)
            
            suggestions.append({
                "id": f"info_{item.get('target')}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "target": target,
                "type": item.get("type", "enhancement"),
                "title": title[:100],
                "description": f"基于 {item.get('source_info', {}).get('source', 'unknown')} 发现",
                "source_info": item.get("source_info", {}),
                "implementation": self._generate_implementation(item),
                "priority": priority,
                "status": "pending",
            })
        
        return suggestions
    
    def _from_project_analysis(self, project: Dict[str, Any]) -> List[Dict]:
        """从项目自分析生成建议"""
        suggestions = []
        
        capabilities = project.get("capabilities", {})
        
        for capability, score in capabilities.items():
            if capability == "overall":
                continue
            
            if score < 0.6:
                suggestions.append({
                    "id": f"proj_{capability}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "target": "project",
                    "type": "capability_enhancement",
                    "title": f"提升 {capability} 能力",
                    "description": f"当前 {capability} 能力评分: {score}",
                    "implementation": f"增加 {capability} 相关模块或功能",
                    "priority": (1.0 - score) * 10,
                    "status": "pending",
                })
        
        health = project.get("health_metrics", {})
        if not health.get("has_tests"):
            suggestions.append({
                "id": f"proj_tests_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "target": "project",
                "type": "test_coverage",
                "title": "添加测试覆盖",
                "description": "项目缺少测试文件",
                "implementation": "添加 tests 目录和测试文件",
                "priority": 5,
                "status": "pending",
            })
        
        return suggestions
    
    def _generate_implementation(self, item: Dict) -> str:
        """生成实现建议"""
        target = item.get("target", "")
        info_type = item.get("type", "")
        
        implementations = {
            ("openhands", "feature_enhancement"): "检查 OpenHands 最新版本，更新功能",
            ("openhands", "new_feature"): "分析 PR，集成新功能到项目",
            ("openspace", "feature_enhancement"): "更新 OpenSpace 到最新版本",
            ("openspace", "version_update"): "升级 OpenSpace 版本",
            ("both", "new_capability"): "分析趋势，添加相关能力",
        }
        
        key = (target, info_type)
        if key in implementations:
            return implementations[key]
        
        return f"分析并集成 {target} 的 {info_type}"
    
    def _deduplicate(self, suggestions: List[Dict]) -> List[Dict]:
        """去重建议"""
        seen = set()
        result = []
        
        for suggestion in suggestions:
            key = f"{suggestion.get('target')}_{suggestion.get('type')}_{suggestion.get('title')[:50]}"
            if key not in seen:
                seen.add(key)
                result.append(suggestion)
        
        return result
    
    def _prioritize(self, suggestions: List[Dict]) -> List[Dict]:
        """排序建议"""
        return sorted(suggestions, key=lambda x: x.get("priority", 0), reverse=True)
    
    def get_suggestions(self) -> List[Dict]:
        """获取当前建议列表"""
        return self._suggestions
    
    def get_pending_suggestions(self) -> List[Dict]:
        """获取待执行的建议"""
        return [s for s in self._suggestions if s.get("status") == "pending"]
    
    def update_status(self, suggestion_id: str, status: str):
        """更新建议状态"""
        for suggestion in self._suggestions:
            if suggestion.get("id") == suggestion_id:
                suggestion["status"] = status
                suggestion["updated_at"] = datetime.now().isoformat()
                
                # 添加到历史
                self._history.append(suggestion.copy())
                self._save_history()
                break
    
    def get_history(self) -> List[Dict]:
        """获取建议历史"""
        return self._history