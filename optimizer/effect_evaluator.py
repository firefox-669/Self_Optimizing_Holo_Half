"""
效果评估器
评估优化效果，决定保留或回退
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime
import json


class EffectEvaluator:
    """
    效果评估器
    评估优化效果，决定是否保留修改
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self._evaluations: List[Dict] = []
        self._load_evaluations()
    
    def _load_evaluations(self):
        """加载评估历史"""
        eval_file = self.workspace / ".sohh_cache" / "effect_evaluations.json"
        if eval_file.exists():
            with open(eval_file, "r", encoding="utf-8") as f:
                self._evaluations = json.load(f)
    
    def _save_evaluations(self):
        """保存评估历史"""
        eval_file = self.workspace / ".sohh_cache" / "effect_evaluations.json"
        eval_file.parent.mkdir(exist_ok=True)
        with open(eval_file, "w", encoding="utf-8") as f:
            json.dump(self._evaluations, f, indent=2, default=str)
    
    async def evaluate(
        self,
        suggestion: Dict[str, Any],
        before_scores: Dict[str, float],
        after_scores: Dict[str, float],
    ) -> Dict[str, Any]:
        """评估优化效果"""
        
        # 计算变化
        changes = {}
        for key in after_scores:
            if key in before_scores:
                delta = after_scores[key] - before_scores[key]
                changes[key] = {
                    "before": before_scores[key],
                    "after": after_scores[key],
                    "delta": round(delta, 3),
                    "improved": delta > 0,
                }
        
        # 计算总分变化
        overall_before = before_scores.get("overall", 0)
        overall_after = after_scores.get("overall", 0)
        overall_delta = overall_after - overall_before
        
        # 决定是否保留
        if overall_delta > 0:
            decision = "keep"
            reason = f"能力提升 {overall_delta:.3f}"
        elif overall_delta == 0:
            decision = "keep"
            reason = "能力无变化"
        else:
            decision = "rollback"
            reason = f"能力下降 {abs(overall_delta):.3f}"
        
        evaluation = {
            "id": f"eval_{len(self._evaluations) + 1}",
            "suggestion_id": suggestion.get("id"),
            "target": suggestion.get("target"),
            "type": suggestion.get("type"),
            "before_scores": before_scores,
            "after_scores": after_scores,
            "overall_delta": round(overall_delta, 3),
            "decision": decision,
            "reason": reason,
            "changes": changes,
            "timestamp": datetime.now().isoformat(),
        }
        
        self._evaluations.append(evaluation)
        self._save_evaluations()
        
        return evaluation
    
    async def evaluate_project_health(
        self,
        before_health: Dict[str, Any],
        after_health: Dict[str, Any],
    ) -> Dict[str, Any]:
        """评估项目健康度变化"""
        
        changes = {}
        
        # 比较各个指标
        for key in after_health:
            if key in before_health:
                if before_health[key] != after_health[key]:
                    changes[key] = {
                        "before": before_health[key],
                        "after": after_health[key],
                    }
        
        # 健康度改进检查
        improved = len(changes) > 0 and any(
            v.get("after", False) and not v.get("before", False)
            for v in changes.values()
        )
        
        return {
            "improved": improved,
            "changes": changes,
            "timestamp": datetime.now().isoformat(),
        }
    
    def should_keep(self, evaluation: Dict[str, Any]) -> bool:
        """判断是否应该保留"""
        return evaluation.get("decision") == "keep"
    
    def should_rollback(self, evaluation: Dict[str, Any]) -> bool:
        """判断是否应该回退"""
        return evaluation.get("decision") == "rollback"
    
    def get_evaluations(self, limit: int = 50) -> List[Dict]:
        """获取评估历史"""
        return self._evaluations[:limit]
    
    def get_recent_decisions(self, days: int = 7) -> Dict[str, int]:
        """获取最近的决策统计"""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        
        decisions = {"keep": 0, "rollback": 0}
        
        for eval_data in self._evaluations:
            timestamp = eval_data.get("timestamp", "")
            if not timestamp:
                continue
            
            try:
                dt = datetime.fromisoformat(timestamp)
                if dt >= cutoff:
                    decision = eval_data.get("decision", "unknown")
                    if decision in decisions:
                        decisions[decision] += 1
            except:
                pass
        
        return decisions
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        if not self._evaluations:
            return 0.0
        
        kept = sum(1 for e in self._evaluations if e.get("decision") == "keep")
        return kept / len(self._evaluations)