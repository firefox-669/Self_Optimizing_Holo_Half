import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from evaluation.custom_rules import CustomScoringRules


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
        
        # 加载自定义评分规则
        self.custom_rules = CustomScoringRules(str(self.workspace))
        
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

    def evaluate(self, execution_history: List[Dict] = None) -> Dict[str, float]:
        """
        评估当前项目能力
        
        Args:
            execution_history: 执行历史记录（可选），用于基于真实使用数据评分
        """
        scores = {}
        
        # 如果有执行历史，使用真实数据评分
        if execution_history and len(execution_history) > 0:
            scores["success_rate"] = self._evaluate_success_rate(execution_history)
            scores["efficiency"] = self._evaluate_efficiency(execution_history)
            scores["user_satisfaction"] = self._evaluate_user_satisfaction(execution_history)
            scores["skill_effectiveness"] = self._evaluate_skill_effectiveness(execution_history)
            scores["error_handling"] = self._evaluate_error_handling(execution_history)
        else:
            # 否则使用静态代码分析（基线评估）
            scores["success_rate"] = self._evaluate_execution()
            scores["efficiency"] = self._evaluate_performance()
            scores["user_satisfaction"] = 0.5  # 默认值
            scores["skill_effectiveness"] = self._evaluate_evolution()
            scores["error_handling"] = self._evaluate_safety()
        
        # 集成度评分（始终基于代码结构）
        if self.custom_rules.is_dimension_enabled("integration"):
            scores["integration"] = self._evaluate_integration()
        
        self._current_scores = scores
        
        # 计算总分（加权平均，支持自定义权重）
        weights = self.custom_rules.get_weights()
        
        overall = sum(scores.get(k, 0) * v for k, v in weights.items())
        
        # 应用自定义规则调整总分
        overall = self.custom_rules.apply_custom_rules(scores, overall)
        
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

    def _evaluate_success_rate(self, execution_history: List[Dict]) -> float:
        """评估任务成功率（基于真实执行数据）"""
        if not execution_history:
            return 0.5
        
        total = len(execution_history)
        successful = sum(1 for exec_rec in execution_history if exec_rec.get("result", {}).get("success", False))
        
        success_rate = successful / total if total > 0 else 0.5
        return round(success_rate, 3)

    def _evaluate_efficiency(self, execution_history: List[Dict]) -> float:
        """评估执行效率（平均执行时间）"""
        if not execution_history:
            return 0.5
        
        durations = []
        for exec_rec in execution_history:
            result = exec_rec.get("result", {})
            if "duration" in result:
                durations.append(result["duration"])
        
        if not durations:
            return 0.5
        
        avg_duration = sum(durations) / len(durations)
        
        # 使用自定义阈值
        excellent_threshold = self.custom_rules.get_threshold("efficiency", "excellent", 60)
        poor_threshold = self.custom_rules.get_threshold("efficiency", "poor", 300)
        
        if avg_duration < excellent_threshold:
            return 1.0
        elif avg_duration > poor_threshold:
            return 0.3
        else:
            return round(1.0 - (avg_duration - excellent_threshold) / (poor_threshold - excellent_threshold) * 0.7, 3)

    def _evaluate_user_satisfaction(self, execution_history: List[Dict]) -> float:
        """评估用户满意度"""
        if not execution_history:
            return 0.5
        
        # 使用自定义阈值
        max_iterations = self.custom_rules.get_threshold("satisfaction", "max_iterations", 50)
        
        satisfaction_scores = []
        for exec_rec in execution_history:
            result = exec_rec.get("result", {})
            if result.get("success"):
                iterations = result.get("iterations", 10)
                sat = max(0.5, 1.0 - (iterations / max_iterations))
                satisfaction_scores.append(sat)
            else:
                satisfaction_scores.append(0.3)
        
        return round(sum(satisfaction_scores) / len(satisfaction_scores), 3) if satisfaction_scores else 0.5

    def _evaluate_skill_effectiveness(self, execution_history: List[Dict]) -> float:
        """评估 Skill 使用效果"""
        if not execution_history:
            return 0.5
        
        skill_improvements = 0
        total_tasks = len(execution_history)
        
        for exec_rec in execution_history:
            result = exec_rec.get("result", {})
            evolution = result.get("evolution", {})
            
            if evolution.get("skills_captured") or evolution.get("optimizations_applied"):
                skill_improvements += 1
        
        if total_tasks == 0:
            return 0.5
        
        effectiveness = skill_improvements / total_tasks
        return round(min(1.0, 0.5 + effectiveness * 0.5), 3)

    def _evaluate_error_handling(self, execution_history: List[Dict]) -> float:
        """评估错误处理能力"""
        if not execution_history:
            return 0.5
        
        errors_occurred = 0
        errors_recovered = 0
        
        for exec_rec in execution_history:
            result = exec_rec.get("result", {})
            if result.get("error"):
                errors_occurred += 1
                if result.get("success"):
                    errors_recovered += 1
        
        if errors_occurred == 0:
            return 1.0
        
        recovery_rate = errors_recovered / errors_occurred
        return round(0.5 + recovery_rate * 0.5, 3)

    def compare_before_after(self, execution_history: List[Dict] = None) -> Dict[str, Any]:
        """
        比较修改前后的能力变化
        
        Args:
            execution_history: 执行历史记录（用于基于真实数据评分）
        """
        if not self._baseline_scores:
            self._baseline_scores = self.evaluate(execution_history)
            self._save_baseline()
        
        current = self.evaluate(execution_history)
        
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