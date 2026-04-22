"""
多维度综合评分引擎

根据 IMPLEMENTATION_PLAN.md 设计:
- 使用活跃度 (25%)
- 任务成功率 (20%)  
- 效率提升 (20%)
- 用户满意度 (20%)
- 成本效益 (10%)
- 创新性 (5%)
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class ComprehensiveScoringSystem:
    """
    多维度综合评分系统
    
    评分维度:
    - 使用活跃度 (25%): 调用频率、活跃用户数、增长率、最近使用
    - 任务成功率 (20%): 执行成功率、错误率、重试次数、手动修正率
    - 效率提升 (20%): 时间节省、Token效率、步骤简化
    - 用户满意度 (20%): 显式评分、隐式反馈、复用率、NPS
    - 成本效益 (10%): Token/任务比、缓存命中率、成本/价值比
    - 创新性 (5%): 功能独特性、技术先进性、填补空白
    """
    
    def __init__(self):
        # 权重配置
        self.weights = {
            "usage_activity": 0.25,
            "success_rate": 0.20,
            "efficiency_gain": 0.20,
            "user_satisfaction": 0.20,
            "cost_efficiency": 0.10,
            "innovation": 0.05
        }
        
        # 决策阈值
        self.thresholds = {
            "keep_and_promote": 0.80,
            "keep": 0.65,
            "keep_with_improvement": 0.50,
            "review": 0.40,
            "rollback": 0.40
        }
    
    def calculate_comprehensive_score(
        self,
        skill_id: str,
        version_metrics: Dict[str, Any],
        baseline_metrics: Optional[Dict[str, Any]] = None,
        period_days: int = 7
    ) -> Dict[str, Any]:
        """
        计算综合评分
        
        Args:
            skill_id: Skill ID
            version_metrics: 当前版本的指标数据
            baseline_metrics: 基线版本指标（用于对比）
            period_days: 统计周期（天）
        
        Returns:
            {
                "overall_score": 0.85,
                "dimension_scores": {
                    "usage_activity": {"score": 0.9, "weight": 0.25, "details": {...}},
                    "success_rate": {"score": 0.8, "weight": 0.20, "details": {...}},
                    ...
                },
                "grade": "A",
                "recommendation": "KEEP_AND_PROMOTE"
            }
        """
        
        # 计算各维度得分
        dimension_scores = {}
        
        # 1. 使用活跃度 (25%)
        dimension_scores["usage_activity"] = self._calc_usage_activity(
            version_metrics, baseline_metrics, period_days
        )
        
        # 2. 任务成功率 (20%)
        dimension_scores["success_rate"] = self._calc_success_rate(
            version_metrics
        )
        
        # 3. 效率提升 (20%)
        dimension_scores["efficiency_gain"] = self._calc_efficiency_gain(
            version_metrics, baseline_metrics
        )
        
        # 4. 用户满意度 (20%)
        dimension_scores["user_satisfaction"] = self._calc_user_satisfaction(
            version_metrics
        )
        
        # 5. 成本效益 (10%)
        dimension_scores["cost_efficiency"] = self._calc_cost_efficiency(
            version_metrics, baseline_metrics
        )
        
        # 6. 创新性 (5%)
        dimension_scores["innovation"] = self._calc_innovation(
            skill_id, version_metrics
        )
        
        # 计算加权总分
        overall_score = sum(
            dimension_scores[dim]["score"] * dimension_scores[dim]["weight"]
            for dim in dimension_scores
        )
        
        # 确定等级和建议
        grade = self._assign_grade(overall_score)
        recommendation = self.make_decision(overall_score)
        
        return {
            "skill_id": skill_id,
            "overall_score": round(overall_score, 4),
            "dimension_scores": dimension_scores,
            "grade": grade,
            "recommendation": recommendation,
            "calculated_at": datetime.now().isoformat()
        }
    
    def _calc_usage_activity(
        self,
        version_metrics: Dict,
        baseline_metrics: Optional[Dict],
        period_days: int
    ) -> Dict[str, Any]:
        """
        计算使用活跃度得分
        
        指标:
        - 调用频率 (40%)
        - 活跃用户数 (30%)
        - 增长率 (20%)
        - 最近使用 (10%)
        """
        total_tasks = version_metrics.get("total_tasks", 0)
        
        if total_tasks == 0:
            return {"score": 0.0, "weight": self.weights["usage_activity"], "details": {}}
        
        # 调用频率得分 (归一化到 0-1)
        # 假设每天 100 次调用为满分
        frequency_score = min(total_tasks / (period_days * 100), 1.0)
        
        # 活跃用户数得分 (如果有数据)
        unique_users = version_metrics.get("unique_users", 1)
        user_score = min(unique_users / 50, 1.0)  # 假设 50 个用户为满分
        
        # 增长率得分 (与基线对比)
        if baseline_metrics:
            baseline_tasks = baseline_metrics.get("total_tasks", 1)
            growth_rate = (total_tasks - baseline_tasks) / max(baseline_tasks, 1)
            growth_score = min(max((growth_rate + 1) / 2, 0), 1.0)  # 归一化
        else:
            growth_score = 0.5  # 无基线时给中等分数
        
        # 最近使用得分
        last_used_days = version_metrics.get("days_since_last_use", 0)
        recency_score = max(1.0 - (last_used_days / period_days), 0)
        
        # 加权计算
        score = (
            frequency_score * 0.4 +
            user_score * 0.3 +
            growth_score * 0.2 +
            recency_score * 0.1
        )
        
        return {
            "score": round(score, 4),
            "weight": self.weights["usage_activity"],
            "details": {
                "frequency_score": round(frequency_score, 4),
                "user_score": round(user_score, 4),
                "growth_score": round(growth_score, 4),
                "recency_score": round(recency_score, 4),
                "total_tasks": total_tasks,
                "unique_users": unique_users
            }
        }
    
    def _calc_success_rate(self, version_metrics: Dict) -> Dict[str, Any]:
        """
        计算任务成功率得分
        
        指标:
        - 执行成功率 (50%)
        - 错误率 (30%)
        - 重试次数 (20%)
        """
        total_tasks = version_metrics.get("total_tasks", 0)
        success_count = version_metrics.get("success_count", 0)
        
        if total_tasks == 0:
            return {"score": 0.0, "weight": self.weights["success_rate"], "details": {}}
        
        # 执行成功率
        success_rate = success_count / total_tasks
        
        # 错误率得分 (越低越好)
        fail_count = version_metrics.get("fail_count", 0)
        error_rate = fail_count / total_tasks
        error_score = 1.0 - error_rate
        
        # 重试次数得分
        avg_retries = version_metrics.get("avg_retries", 0)
        retry_score = max(1.0 - (avg_retries / 5), 0)  # 假设平均 5 次重试为 0 分
        
        # 加权计算
        score = (
            success_rate * 0.5 +
            error_score * 0.3 +
            retry_score * 0.2
        )
        
        return {
            "score": round(score, 4),
            "weight": self.weights["success_rate"],
            "details": {
                "success_rate": round(success_rate, 4),
                "error_rate": round(error_rate, 4),
                "retry_score": round(retry_score, 4),
                "success_count": success_count,
                "fail_count": fail_count
            }
        }
    
    def _calc_efficiency_gain(
        self,
        version_metrics: Dict,
        baseline_metrics: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        计算效率提升得分
        
        指标:
        - 时间节省 (50%)
        - Token 效率 (30%)
        - 步骤简化 (20%)
        """
        if not baseline_metrics:
            return {"score": 0.5, "weight": self.weights["efficiency_gain"], "details": {"note": "No baseline"}}
        
        # 时间节省
        baseline_duration = baseline_metrics.get("avg_duration", 1)
        current_duration = version_metrics.get("avg_duration", 1)
        
        if baseline_duration > 0:
            time_improvement = (baseline_duration - current_duration) / baseline_duration
            time_score = min(max(time_improvement + 0.5, 0), 1.0)  # 归一化到 0-1
        else:
            time_score = 0.5
        
        # Token 效率
        baseline_tokens = baseline_metrics.get("avg_tokens", 1)
        current_tokens = version_metrics.get("avg_tokens", 1)
        
        if baseline_tokens > 0:
            token_improvement = (baseline_tokens - current_tokens) / baseline_tokens
            token_score = min(max(token_improvement + 0.5, 0), 1.0)
        else:
            token_score = 0.5
        
        # 步骤简化 (如果有数据)
        baseline_steps = baseline_metrics.get("avg_steps", 10)
        current_steps = version_metrics.get("avg_steps", 10)
        
        if baseline_steps > 0:
            steps_improvement = (baseline_steps - current_steps) / baseline_steps
            steps_score = min(max(steps_improvement + 0.5, 0), 1.0)
        else:
            steps_score = 0.5
        
        # 加权计算
        score = (
            time_score * 0.5 +
            token_score * 0.3 +
            steps_score * 0.2
        )
        
        return {
            "score": round(score, 4),
            "weight": self.weights["efficiency_gain"],
            "details": {
                "time_score": round(time_score, 4),
                "token_score": round(token_score, 4),
                "steps_score": round(steps_score, 4),
                "duration_improvement": f"{(time_score - 0.5) * 200:.1f}%",
                "token_improvement": f"{(token_score - 0.5) * 200:.1f}%"
            }
        }
    
    def _calc_user_satisfaction(self, version_metrics: Dict) -> Dict[str, Any]:
        """
        计算用户满意度得分
        
        指标:
        - 显式评分 (50%)
        - 隐式反馈 (30%)
        - 复用率 (20%)
        """
        # 显式评分 (1-5星转换为 0-1)
        avg_rating = version_metrics.get("avg_rating", 3.0)
        explicit_score = (avg_rating - 1) / 4  # 1星=0, 5星=1
        
        # 隐式反馈得分
        implicit_feedback = version_metrics.get("implicit_feedback_avg", 3.0)
        implicit_score = (implicit_feedback - 1) / 4
        
        # 复用率
        reuse_rate = version_metrics.get("reuse_rate", 0.5)
        
        # 加权计算
        score = (
            explicit_score * 0.5 +
            implicit_score * 0.3 +
            reuse_rate * 0.2
        )
        
        return {
            "score": round(score, 4),
            "weight": self.weights["user_satisfaction"],
            "details": {
                "explicit_score": round(explicit_score, 4),
                "implicit_score": round(implicit_score, 4),
                "reuse_rate": round(reuse_rate, 4),
                "avg_rating": avg_rating
            }
        }
    
    def _calc_cost_efficiency(
        self,
        version_metrics: Dict,
        baseline_metrics: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        计算成本效益得分
        
        指标:
        - Token/任务比 (60%)
        - 成本/价值比 (40%)
        """
        # Token/任务比
        total_tokens = version_metrics.get("total_tokens", 0)
        total_tasks = version_metrics.get("total_tasks", 1)
        tokens_per_task = total_tokens / max(total_tasks, 1)
        
        # 与基线对比
        if baseline_metrics:
            baseline_tokens_per_task = baseline_metrics.get("avg_tokens", tokens_per_task)
            if baseline_tokens_per_task > 0:
                cost_improvement = (baseline_tokens_per_task - tokens_per_task) / baseline_tokens_per_task
                token_efficiency_score = min(max(cost_improvement + 0.5, 0), 1.0)
            else:
                token_efficiency_score = 0.5
        else:
            # 无基线时，假设 2000 tokens/task 为中等
            token_efficiency_score = min(max(1.0 - (tokens_per_task / 4000), 0), 1.0)
        
        # 成本/价值比 (简化版：基于成功率和评分)
        success_rate = version_metrics.get("success_rate", 0.5)
        avg_rating = version_metrics.get("avg_rating", 3.0)
        value_score = (success_rate * 0.6 + ((avg_rating - 1) / 4) * 0.4)
        
        # 加权计算
        score = (
            token_efficiency_score * 0.6 +
            value_score * 0.4
        )
        
        return {
            "score": round(score, 4),
            "weight": self.weights["cost_efficiency"],
            "details": {
                "token_efficiency_score": round(token_efficiency_score, 4),
                "value_score": round(value_score, 4),
                "tokens_per_task": round(tokens_per_task, 2)
            }
        }
    
    def _calc_innovation(self, skill_id: str, version_metrics: Dict) -> Dict[str, Any]:
        """
        计算创新性得分
        
        指标:
        - 功能独特性 (40%)
        - 技术先进性 (30%)
        - 填补空白 (30%)
        """
        # 这里需要更复杂的分析，暂时使用启发式方法
        
        # 功能独特性：检查是否是全新功能
        is_new_feature = version_metrics.get("is_new_feature", False)
        uniqueness_score = 0.8 if is_new_feature else 0.4
        
        # 技术先进性：基于元数据中的技术标签
        tech_tags = version_metrics.get("tech_tags", [])
        advanced_techs = ["ai", "ml", "nlp", "transformer", "llm"]
        advanced_count = sum(1 for tag in tech_tags if tag.lower() in advanced_techs)
        advancement_score = min(advanced_count / 3, 1.0)
        
        # 填补空白：是否解决了之前无法解决的问题
        fills_gap = version_metrics.get("fills_capability_gap", False)
        gap_score = 0.9 if fills_gap else 0.3
        
        # 加权计算
        score = (
            uniqueness_score * 0.4 +
            advancement_score * 0.3 +
            gap_score * 0.3
        )
        
        return {
            "score": round(score, 4),
            "weight": self.weights["innovation"],
            "details": {
                "uniqueness_score": round(uniqueness_score, 4),
                "advancement_score": round(advancement_score, 4),
                "gap_score": round(gap_score, 4),
                "is_new_feature": is_new_feature,
                "fills_gap": fills_gap
            }
        }
    
    def _assign_grade(self, score: float) -> str:
        """根据分数分配等级"""
        if score >= 0.90:
            return "S"
        elif score >= 0.80:
            return "A"
        elif score >= 0.70:
            return "B"
        elif score >= 0.60:
            return "C"
        elif score >= 0.50:
            return "D"
        else:
            return "F"
    
    def make_decision(self, score: float) -> str:
        """
        根据评分做决策
        
        Returns:
            "KEEP_AND_PROMOTE" (≥0.80)
            "KEEP" (≥0.65)
            "KEEP_WITH_IMPROVEMENT" (≥0.50)
            "REVIEW" (≥0.40)
            "ROLLBACK" (<0.40)
        """
        if score >= self.thresholds["keep_and_promote"]:
            return "KEEP_AND_PROMOTE"
        elif score >= self.thresholds["keep"]:
            return "KEEP"
        elif score >= self.thresholds["keep_with_improvement"]:
            return "KEEP_WITH_IMPROVEMENT"
        elif score >= self.thresholds["review"]:
            return "REVIEW"
        else:
            return "ROLLBACK"


# 便捷函数
def calculate_skill_score(
    skill_id: str,
    version_metrics: Dict,
    baseline_metrics: Dict = None
) -> Dict:
    """快速计算 Skill 评分"""
    scorer = ComprehensiveScoringSystem()
    return scorer.calculate_comprehensive_score(skill_id, version_metrics, baseline_metrics)


if __name__ == "__main__":
    # 测试评分系统
    scorer = ComprehensiveScoringSystem()
    
    # 模拟数据
    version_metrics = {
        "total_tasks": 156,
        "success_count": 143,
        "fail_count": 13,
        "avg_duration": 38.5,
        "avg_tokens": 1150,
        "avg_rating": 4.6,
        "unique_users": 45,
        "days_since_last_use": 1,
        "total_tokens": 179400,
        "success_rate": 0.92,
        "reuse_rate": 0.75,
        "implicit_feedback_avg": 4.3,
        "is_new_feature": True,
        "tech_tags": ["ai", "automation"],
        "fills_capability_gap": True
    }
    
    baseline_metrics = {
        "total_tasks": 120,
        "avg_duration": 45.2,
        "avg_tokens": 1350,
        "avg_rating": 4.2
    }
    
    result = scorer.calculate_comprehensive_score(
        "code_review_v2",
        version_metrics,
        baseline_metrics
    )
    
    print("=" * 60)
    print("Comprehensive Scoring Result")
    print("=" * 60)
    print(f"Overall Score: {result['overall_score']}")
    print(f"Grade: {result['grade']}")
    print(f"Recommendation: {result['recommendation']}")
    print("\nDimension Scores:")
    for dim, data in result['dimension_scores'].items():
        print(f"  {dim}: {data['score']} (weight: {data['weight']})")
