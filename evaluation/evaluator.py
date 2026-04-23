import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class CapabilityEvaluator:
    """
    能力评估器
    评估项目修改前后的能力变化，决定保留或回滚
    """

    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self._baseline_scores: Dict[str, float] = {}
        self._current_scores: Dict[str, float] = {}
        self._evaluation_history: List[Dict] = []
        
        self._load_baseline()

    def _load_baseline(self):
        """加载基线分数"""
        baseline_file = self.workspace / ".sohh_cache" / "capability_baseline.json"
        if baseline_file.exists():
            import json
            with open(baseline_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._baseline_scores = data.get("baseline", {})

    def _save_baseline(self):
        """保存基线分数"""
        baseline_file = self.workspace / ".sohh_cache" / "capability_baseline.json"
        baseline_file.parent.mkdir(exist_ok=True)
        import json
        with open(baseline_file, "w", encoding="utf-8") as f:
            json.dump({
                "baseline": self._baseline_scores,
                "updated": datetime.now().isoformat(),
            }, f, indent=2)

    def evaluate(self) -> Dict[str, float]:
        """
        评估当前项目能力
        """
        scores = {}
        
        scores["execution"] = self._evaluate_execution()
        scores["evolution"] = self._evaluate_evolution()
        scores["safety"] = self._evaluate_safety()
        scores["integration"] = self._evaluate_integration()
        scores["performance"] = self._evaluate_performance()
        
        self._current_scores = scores
        
        overall = sum(scores.values()) / len(scores) if scores else 0.0
        scores["overall"] = round(overall, 3)
        
        return scores

    def _evaluate_execution(self) -> float:
        """评估执行能力"""
        score = 0.5
        
        self_dir = self.workspace / "Self_Optimizing_Holo_Half"
        
        if (self_dir / "executor").exists():
            score += 0.2
        
        executor_file = self_dir / "executor" / "executor.py"
        if executor_file.exists():
            content = executor_file.read_text(encoding="utf-8")
            if "async def execute" in content:
                score += 0.15
            if "OpenHands" in content:
                score += 0.1
        
        return min(1.0, score)

    def _evaluate_evolution(self) -> float:
        """评估进化能力"""
        score = 0.5
        
        self_dir = self.workspace / "Self_Optimizing_Holo_Half"
        
        if (self_dir / "evolution").exists():
            score += 0.2
        
        evolver_file = self_dir / "evolution" / "evolver.py"
        if evolver_file.exists():
            content = evolver_file.read_text(encoding="utf-8")
            if "async def evolve" in content:
                score += 0.15
            if "self_modify" in content:
                score += 0.1
            if "self_heal" in content:
                score += 0.1
        
        return min(1.0, score)

    def _evaluate_safety(self) -> float:
        """评估安全能力"""
        score = 0.5
        
        self_dir = self.workspace / "Self_Optimizing_Holo_Half"
        
        if (self_dir / "monitor").exists():
            score += 0.2
        
        safety_file = self_dir / "monitor" / "safety.py"
        if safety_file.exists():
            content = safety_file.read_text(encoding="utf-8")
            if "dangerous_patterns" in content:
                score += 0.15
            if "max_execution_time" in content:
                score += 0.1
        
        return min(1.0, score)

    def _evaluate_integration(self) -> float:
        """评估集成能力"""
        score = 0.5
        
        self_dir = self.workspace / "Self_Optimizing_Holo_Half"
        
        modules = ["executor", "evolution", "monitor", "ai_news", "patches", "evaluation"]
        existing = sum(1 for m in modules if (self_dir / m).exists())
        score += existing * 0.08
        
        return min(1.0, score)

    def _evaluate_performance(self) -> float:
        """评估性能"""
        score = 0.7
        
        self_dir = self.workspace / "Self_Optimizing_Holo_Half"
        
        all_py_files = list(self_dir.glob("**/*.py"))
        for py_file in all_py_files:
            if py_file.name == "__init__.py":
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                if "except Exception:" in content and "pass" not in content:
                    score += 0.01
            except Exception:
                pass
        
        return min(1.0, score)

    def compare_before_after(self) -> Dict[str, Any]:
        """
        比较修改前后的能力变化
        """
        if not self._baseline_scores:
            self._baseline_scores = self.evaluate()
            self._save_baseline()
        
        current = self.evaluate()
        
        changes = {}
        for key in current:
            if key in self._baseline_scores:
                delta = current[key] - self._baseline_scores[key]
                changes[key] = {
                    "before": self._baseline_scores[key],
                    "after": current[key],
                    "delta": round(delta, 3),
                    "improved": delta > 0,
                }
        
        overall_before = self._baseline_scores.get("overall", 0)
        overall_after = current.get("overall", 0)
        improved = overall_after >= overall_before
        
        result = {
            "improved": improved,
            "overall_before": overall_before,
            "overall_after": overall_after,
            "delta": round(overall_after - overall_before, 3),
            "changes": changes,
            "timestamp": datetime.now().isoformat(),
        }
        
        self._evaluation_history.append(result)
        
        if improved:
            self._baseline_scores = current.copy()
            self._save_baseline()
        
        return result

    def get_history(self) -> List[Dict]:
        """获取评估历史"""
        return self._evaluation_history

    def set_baseline(self, scores: Dict[str, float]):
        """设置基线"""
        self._baseline_scores = scores
        self._save_baseline()

    def get_baseline(self) -> Dict[str, float]:
        """获取基线"""
        return self._baseline_scores