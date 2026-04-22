"""
自我进化循环
整合所有模块，实现边用边进化的核心循环
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

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


class SelfEvolutionLoop:
    """
    自我进化循环
    整合所有模块，实现边用边进化
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        
        # 集成模块
        self.openhands_client = OpenHandsClient(str(self.workspace))
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
        
        # 报告生成器
        self.daily_report = DailyReportGenerator(str(self.workspace))
        self.deep_analyzer = DeepAnalyzer(str(self.workspace))
        
        # 状态
        self._running = False
        self._baseline_scores: Dict[str, float] = {}
        self._last_cycle = None
    
    async def initialize(self):
        """初始化所有模块"""
        # 连接外部服务
        await self.openhands_client.connect()
        await self.openspace_client.connect()
        
        # 获取基线
        self._baseline_scores = await self._get_baseline_scores()
    
    async def _get_baseline_scores(self) -> Dict[str, float]:
        """获取能力基线"""
        return {
            "execution": 0.5,
            "evolution": 0.5,
            "safety": 0.5,
            "integration": 0.5,
            "self_analysis": 0.5,
            "overall": 0.5,
        }
    
    async def run_daily_cycle(self) -> Dict[str, Any]:
        """
        运行每日进化循环
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "status": "started",
        }
        
        try:
            # 1. 能力分析
            results["analysis"] = await self._run_analysis()
            
            # 2. 生成建议
            results["suggestions"] = await self._generate_suggestions(
                results["analysis"]
            )
            
            # 3. 评估建议
            pending = [
                s for s in results["suggestions"]
                if s.get("status") == "pending"
            ]
            results["pending_count"] = len(pending)
            
            # 4. 应用高优先级建议
            applied = await self._apply_high_priority(pending[:3])
            results["applied"] = applied
            
            # 5. 评估效果
            if applied:
                new_scores = await self._evaluate_after_optimization()
                comparison = await self.optimizer.compare_with_baseline(
                    self._baseline_scores,
                    new_scores,
                )
                results["comparison"] = comparison
                
                # 记录变更
                self.change_logger.log_capability_change(
                    "overall",
                    self._baseline_scores.get("overall", 0),
                    new_scores.get("overall", 0),
                )
                
                # 更新基线
                if comparison.get("improved"):
                    self._baseline_scores = new_scores.copy()
            
            # 6. 生成报告
            results["daily_report"] = await self.daily_report.generate(
                execution_stats=results.get("execution_stats"),
                evolution_stats=results.get("evolution_stats"),
                suggestions=results.get("suggestions"),
                health=results.get("analysis", {}).get("project", {}).get("health_metrics"),
            )
            
            results["deep_analysis"] = await self.deep_analyzer.analyze(
                existing_analysis=results["analysis"].get("existing"),
                project_analysis=results["analysis"].get("project"),
                info_analysis=results["analysis"].get("info"),
            )
            
            results["status"] = "completed"
            self._last_cycle = datetime.now()
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    async def _run_analysis(self) -> Dict[str, Any]:
        """运行所有分析"""
        analysis = {
            "existing": {},
            "project": {},
            "info": [],
        }
        
        # 并行分析
        oh_analysis = await self.oh_analyzer.analyze()
        os_analysis = await self.os_analyzer.analyze()
        project_analysis = await self.project_analyzer.analyze()
        info_results = await self.info_collector.collect_all()
        
        analysis["existing"] = {
            "openhands": oh_analysis,
            "openspace": os_analysis,
        }
        analysis["project"] = project_analysis
        analysis["info"] = info_results.get("openhands", []) + info_results.get("openspace", [])
        
        # 收集建议
        self.info_collector.analyze_improvements()
        
        return analysis
    
    async def _generate_suggestions(
        self,
        analysis: Dict[str, Any],
    ) -> List[Dict]:
        """生成 Evolution Suggestions"""
        
        # 资讯分析
        info_analysis = analysis.get("info", [])
        project_analysis = analysis.get("project", {})
        
        suggestions = await self.suggestion_engine.generate_suggestions(
            existing_analysis=analysis.get("existing"),
            info_analysis=info_analysis,
            project_analysis=project_analysis,
        )
        
        return suggestions
    
    async def _apply_high_priority(
        self,
        suggestions: List[Dict],
    ) -> List[Dict]:
        """应用高优先级建议"""
        applied = []
        
        for suggestion in suggestions:
            priority = suggestion.get("priority", 0)
            if priority < 7:
                continue
            
            # 评估建议
            if not await self.optimizer.evaluate_suggestion(suggestion):
                continue
            
            # 创建快照
            snapshot_id = await self.snapshot_manager.create_snapshot(
                description=f"Pre-optimization: {suggestion.get('title')}",
                tags=["optimization"],
            )
            
            # 应用优化
            result = await self.optimizer.apply_optimization(suggestion)
            
            if result.get("applied"):
                applied.append({
                    "suggestion": suggestion,
                    "snapshot_id": snapshot_id,
                    "result": result,
                })
                
                # 记录变更
                self.change_logger.log_optimization(
                    suggestion,
                    "applied",
                    self._baseline_scores.get("overall", 0),
                    None,
                )
            else:
                # 回退
                await self.snapshot_manager.restore_snapshot(snapshot_id)
        
        return applied
    
    async def _evaluate_after_optimization(self) -> Dict[str, float]:
        """评估优化后的能力"""
        # 重新分析
        project_analysis = await self.project_analyzer.analyze()
        return project_analysis.get("capabilities", self._baseline_scores)
    
    async def run_continuously(
        self,
        interval_hours: int = 24,
    ) -> None:
        """持续运行"""
        self._running = True
        
        while self._running:
            await self.run_daily_cycle()
            await asyncio.sleep(interval_hours * 3600)
    
    def stop(self):
        """停止"""
        self._running = False
    
    async def close(self):
        """关闭"""
        await self.openhands_client.close()
        await self.openspace_client.close()
        await self.info_collector.close()
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "running": self._running,
            "last_cycle": self._last_cycle.isoformat() if self._last_cycle else None,
            "baseline_scores": self._baseline_scores,
            "openhands_connected": self.openhands_client.is_connected(),
            "openspace_connected": self.openspace_client.is_connected(),
        }