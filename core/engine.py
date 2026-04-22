"""
Self_Optimizing_Holo_Half 核心引擎
真实集成OpenHands + 真实集成OpenSpace + 自我进化系统
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

from executor.executor import OpenHandsExecutor
from evolution.evolver import EvoEngine
from monitor.safety import SafetyMonitor
from patches.fixes import PatchManager
from ai_news.integrator import NewsIntegrator
from evaluation.evaluator import CapabilityEvaluator

from integrations.openhands import OpenHandsClient
from integrations.openspace import OpenSpaceClient
from analyzer import (
    OpenHandsAnalyzer,
    OpenSpaceAnalyzer,
    ProjectSelfAnalyzer,
    InfoCollector,
)
from evolution.suggestion_engine import EvolutionSuggestionEngine
from version_control import SnapshotManager, ChangeLogger, RollbackManager
from optimizer import AutoOptimizer, EffectEvaluator
from reporting import DailyReportGenerator, DeepAnalyzer
from core.evolution_loop import SelfEvolutionLoop


class SelfOptimizingEngine:
    """
    自进化智能编程引擎
    整合 OpenHands + OpenSpace + 自我进化系统
    """
    
    def __init__(
        self,
        workspace: str,
        openhands_url: str = "http://localhost:3000",
        enable_evolution: bool = True,
        enable_safety_monitor: bool = True,
        enable_ai_news: bool = True,
        enable_self_evolution: bool = True,
    ):
        self.workspace = Path(workspace)
        self.openhands_url = openhands_url
        self.enable_evolution = enable_evolution
        self.enable_safety_monitor = enable_safety_monitor
        self.enable_ai_news = enable_ai_news
        self.enable_self_evolution = enable_self_evolution
        
        # 原有组件
        self.executor = OpenHandsExecutor(openhands_url, str(self.workspace))
        self.evolver = EvoEngine(str(self.workspace)) if enable_evolution else None
        self.safety_monitor = SafetyMonitor() if enable_safety_monitor else None
        self.patch_manager = PatchManager(str(self.workspace))
        self.news_integrator = NewsIntegrator() if enable_ai_news else None
        self.evaluator = CapabilityEvaluator(str(self.workspace))
        
        # 新集成的组件
        self.openhands_client = OpenHandsClient(str(self.workspace), openhands_url)
        self.openspace_client = OpenSpaceClient(str(self.workspace))
        
        # 分析器
        self.oh_analyzer = OpenHandsAnalyzer(self.openhands_client)
        self.os_analyzer = OpenSpaceAnalyzer(self.openspace_client)
        self.project_analyzer = ProjectSelfAnalyzer(str(self.workspace))
        self.info_collector = InfoCollector(str(self.workspace))
        
        # 建议引擎
        self.suggestion_engine = EvolutionSuggestionEngine(str(self.workspace))
        
        # 版本控制
        self.snapshot_manager = SnapshotManager(str(self.workspace))
        self.change_logger = ChangeLogger(str(self.workspace))
        self.rollback_manager = RollbackManager(str(self.workspace))
        
        # 优化器
        self.optimizer = AutoOptimizer(str(self.workspace))
        self.effect_evaluator = EffectEvaluator(str(self.workspace))
        
        # 报告
        self.daily_report = DailyReportGenerator(str(self.workspace))
        self.deep_analyzer = DeepAnalyzer(str(self.workspace))
        
        # 自我进化循环
        self.evolution_loop = SelfEvolutionLoop(str(self.workspace)) if enable_self_evolution else None
        
        self._execution_history: List[Dict] = []
        
        self._openspace_connected = False
        if self.evolver and hasattr(self.evolver, 'is_connected'):
            try:
                self._openspace_connected = self.evolver.is_connected()
            except:
                pass
    
    async def __aenter__(self):
        await self.openhands_client.connect()
        await self.openspace_client.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()
        return False
    
    async def execute(
        self,
        task: str,
        project_context: Optional[Dict[str, Any]] = None,
        max_iterations: int = 20,
    ) -> Dict[str, Any]:
        context = project_context or {}
        context["task"] = task
        context["workspace"] = str(self.workspace)
        
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if self.enable_safety_monitor:
            await self.safety_monitor.start_monitoring(execution_id)
        
        if self.enable_ai_news:
            latest_trends = await self.news_integrator.fetch_latest()
            context["ai_trends"] = latest_trends
        
        context = self.patch_manager.apply_compatible_patches(context)
        
        result = await self.executor.execute(
            task=task,
            workspace=self.workspace,
            max_iterations=max_iterations,
        )
        
        execution_record = {
            "id": execution_id,
            "task": task,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "context": context,
        }
        self._execution_history.append(execution_record)
        
        if self.enable_safety_monitor:
            await self.safety_monitor.check_execution_safety(execution_id, result)
        
        if self.enable_evolution and result.get("success"):
            evolution_result = await self.evolver.evolve(
                execution_record=execution_record,
                context=context,
            )
            result["evolution"] = evolution_result
        
        if self.enable_safety_monitor:
            await self.safety_monitor.stop_monitoring(execution_id)
        
        return result
    
    async def evolve_self(self) -> Dict[str, Any]:
        if not self.evolver:
            return {"success": False}

        result = await self.evolver.evolve_self()
        
        return {
            "success": True,
            "result": result,
            "openspace_connected": self._openspace_connected,
        }

    async def evolve_project_skills(
        self,
        project_path: str,
    ) -> Dict[str, Any]:
        if not self.evolver:
            return {"success": False}

        return await self.evolver.evolve_project_skills(project_path)
    
    async def run_self_evolution_cycle(self) -> Dict[str, Any]:
        """运行自我进化循环"""
        if not self.evolution_loop:
            return {"success": False, "reason": "Self evolution not enabled"}
        
        result = await self.evolution_loop.run_daily_cycle()
        return result
    
    async def run_deep_analysis(self) -> Dict[str, Any]:
        """运行深度分析"""
        oh_analysis = await self.oh_analyzer.analyze()
        os_analysis = await self.os_analyzer.analyze()
        project_analysis = await self.project_analyzer.analyze()
        info_results = await self.info_collector.collect_all()
        
        info_improvements = self.info_collector.analyze_improvements()
        
        result = await self.deep_analyzer.analyze(
            existing_analysis={"openhands": oh_analysis, "openspace": os_analysis},
            project_analysis=project_analysis,
            info_analysis=info_improvements,
        )
        
        return result
    
    def get_stability_report(self) -> Dict[str, Any]:
        evolution_log = self.evolver.get_evolution_log() if self.evolver else []
        
        return {
            "overall_stability": 1.0 if self._openspace_connected else 0.3,
            "connections": {
                "openspace": self._openspace_connected,
                "openhands": self.executor._connected if self.executor else False,
            },
            "modifications": len(evolution_log),
        }

    async def learn_and_evolve(self) -> Dict[str, Any]:
        trends = await self.news_integrator.fetch_latest()
        improvements = self.news_integrator.analyze_improvements()
        before_scores = self.evaluator.evaluate()
        comparison = self.evaluator.compare_before_after()
        return {
            "trends_count": len(trends),
            "improvements_found": len(improvements),
            "before_scores": before_scores,
            "comparison": comparison,
            "success": comparison.get("improved", False),
        }

    async def full_self_evolution(self) -> Dict[str, Any]:
        result = await self.learn_and_evolve()
        if result.get("success"):
            self_evo = await self.evolve_self()
            result["self_evolution"] = self_evo
        stability = self.get_stability_report()
        result["stability"] = stability
        return result
    
    async def get_capability_scores(self) -> Dict[str, float]:
        """获取能力评分"""
        project_analysis = await self.project_analyzer.analyze()
        return project_analysis.get("capabilities", {})
    
    async def get_suggestions(self) -> List[Dict]:
        """获取 Evolution Suggestions"""
        oh_analysis = await self.oh_analyzer.analyze()
        os_analysis = await self.os_analyzer.analyze()
        project_analysis = await self.project_analyzer.analyze()
        info_results = await self.info_collector.collect_all()
        
        info_improvements = self.info_collector.analyze_improvements()
        
        suggestions = await self.suggestion_engine.generate_suggestions(
            existing_analysis={"openhands": oh_analysis, "openspace": os_analysis},
            info_analysis=info_improvements,
            project_analysis=project_analysis,
        )
        
        return suggestions
    
    async def shutdown(self):
        if self.safety_monitor:
            await self.safety_monitor.shutdown()
        if self.news_integrator:
            await self.news_integrator.close()
        if self.executor:
            await self.executor.close()
        if self.evolver:
            await self.evolver.shutdown()
        if self.openhands_client:
            await self.openhands_client.close()
        if self.openspace_client:
            await self.openspace_client.close()
        if self.info_collector:
            await self.info_collector.close()
        if self.evolution_loop:
            await self.evolution_loop.close()
    
    def get_execution_history(self) -> List[Dict]:
        return self._execution_history
    
    def get_evolution_stats(self) -> Dict[str, Any]:
        if not self.evolver:
            return {"enabled": False}
        
        log = self.evolver.get_evolution_log()
        return {
            "total_evolutions": len(log),
            "connected": self._openspace_connected,
        }
    
    def get_safety_status(self) -> Dict[str, Any]:
        if not self.safety_monitor:
            return {"enabled": False}
        
        return {
            "active_executions": len(self.safety_monitor.get_active_executions()),
            "safety_logs": len(self.safety_monitor.get_safety_logs()),
        }
    
    def get_information_gaps(self) -> List[Dict]:
        if not self.news_integrator:
            return []
        return self.news_integrator.get_unimplemented_features()