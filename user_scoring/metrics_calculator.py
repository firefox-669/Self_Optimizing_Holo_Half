"""
指标计算器

从原始数据中计算各种性能指标
为评分引擎提供标准化的指标数据
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import statistics


class MetricsCalculator:
    """
    指标计算器
    
    计算的指标包括:
    - 基础指标: 任务数、成功率、平均耗时等
    - 趋势指标: 增长率、变化率
    - 质量指标: 用户满意度、NPS
    - 效率指标: Token 效率、缓存命中率
    """
    
    @staticmethod
    def calculate_basic_metrics(task_records: List[Dict]) -> Dict[str, Any]:
        """
        计算基础指标
        
        Args:
            task_records: 任务执行记录列表
        
        Returns:
            {
                "total_tasks": 156,
                "success_count": 143,
                "fail_count": 13,
                "success_rate": 0.92,
                "avg_duration": 45.2,
                "median_duration": 42.0,
                "p95_duration": 78.5,
                "avg_tokens": 1234,
                "total_tokens": 192504,
                ...
            }
        """
        if not task_records:
            return {
                "total_tasks": 0,
                "success_count": 0,
                "fail_count": 0,
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "median_duration": 0.0,
                "p95_duration": 0.0,
                "avg_tokens": 0,
                "total_tokens": 0
            }
        
        total = len(task_records)
        success_count = sum(1 for t in task_records if t.get("status") == "success")
        fail_count = total - success_count
        
        durations = [t.get("duration_seconds", 0) for t in task_records if t.get("duration_seconds")]
        tokens = [t.get("tokens_used", 0) for t in task_records if t.get("tokens_used")]
        
        # 计算统计量
        avg_duration = statistics.mean(durations) if durations else 0
        median_duration = statistics.median(durations) if durations else 0
        p95_duration = sorted(durations)[int(len(durations) * 0.95)] if durations else 0
        
        avg_tokens = statistics.mean(tokens) if tokens else 0
        total_tokens = sum(tokens)
        
        return {
            "total_tasks": total,
            "success_count": success_count,
            "fail_count": fail_count,
            "success_rate": success_count / max(total, 1),
            "avg_duration": round(avg_duration, 2),
            "median_duration": round(median_duration, 2),
            "p95_duration": round(p95_duration, 2),
            "std_duration": round(statistics.stdev(durations), 2) if len(durations) > 1 else 0,
            "avg_tokens": round(avg_tokens, 2),
            "total_tokens": total_tokens,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0
        }
    
    @staticmethod
    def calculate_trend_metrics(
        current_period: List[Dict],
        previous_period: List[Dict]
    ) -> Dict[str, Any]:
        """
        计算趋势指标（与上一周期对比）
        
        Args:
            current_period: 当前周期的任务记录
            previous_period: 上一周期的任务记录
        
        Returns:
            {
                "task_growth_rate": 0.15,  # 15% 增长
                "success_rate_change": 0.05,  # 成功率提升 5%
                "duration_change": -0.10,  # 耗时减少 10%
                "token_change": -0.08,  # Token 消耗减少 8%
                ...
            }
        """
        current_metrics = MetricsCalculator.calculate_basic_metrics(current_period)
        previous_metrics = MetricsCalculator.calculate_basic_metrics(previous_period)
        
        # 计算变化率
        def calc_change_rate(current, previous):
            if previous == 0:
                return 0.0
            return (current - previous) / previous
        
        return {
            "task_growth_rate": round(calc_change_rate(
                current_metrics["total_tasks"],
                previous_metrics["total_tasks"]
            ), 4),
            "success_rate_change": round(calc_change_rate(
                current_metrics["success_rate"],
                previous_metrics["success_rate"]
            ), 4),
            "duration_change": round(calc_change_rate(
                current_metrics["avg_duration"],
                previous_metrics["avg_duration"]
            ), 4),
            "token_change": round(calc_change_rate(
                current_metrics["avg_tokens"],
                previous_metrics["avg_tokens"]
            ), 4),
            "current_metrics": current_metrics,
            "previous_metrics": previous_metrics
        }
    
    @staticmethod
    def calculate_quality_metrics(
        task_records: List[Dict],
        feedback_records: List[Dict]
    ) -> Dict[str, Any]:
        """
        计算质量指标
        
        Args:
            task_records: 任务执行记录
            feedback_records: 用户反馈记录
        
        Returns:
            {
                "avg_rating": 4.5,
                "rating_distribution": {1: 2, 2: 5, 3: 10, 4: 30, 5: 109},
                "nps_score": 65,
                "complaint_rate": 0.05,
                ...
            }
        """
        if not feedback_records:
            return {
                "avg_rating": 0.0,
                "rating_distribution": {},
                "nps_score": 0,
                "complaint_rate": 0.0
            }
        
        # 评分分布
        ratings = [f.get("rating", 0) for f in feedback_records]
        rating_dist = {}
        for r in range(1, 6):
            rating_dist[r] = ratings.count(r)
        
        # 平均评分
        avg_rating = statistics.mean(ratings) if ratings else 0
        
        # NPS (Net Promoter Score)
        promoters = sum(1 for r in ratings if r >= 4)
        detractors = sum(1 for r in ratings if r <= 2)
        total_respondents = len(ratings)
        nps = ((promoters - detractors) / max(total_respondents, 1)) * 100
        
        # 投诉率 (1-2星视为投诉)
        complaint_rate = detractors / max(total_respondents, 1)
        
        return {
            "avg_rating": round(avg_rating, 2),
            "rating_distribution": rating_dist,
            "nps_score": round(nps, 2),
            "complaint_rate": round(complaint_rate, 4),
            "total_feedbacks": total_respondents,
            "promoters": promoters,
            "detractors": detractors
        }
    
    @staticmethod
    def calculate_efficiency_metrics(
        task_records: List[Dict],
        baseline_avg_tokens: float = None
    ) -> Dict[str, Any]:
        """
        计算效率指标
        
        Args:
            task_records: 任务执行记录
            baseline_avg_tokens: 基线平均 Token 消耗
        
        Returns:
            {
                "tokens_per_task": 1234,
                "token_efficiency_score": 0.85,
                "cache_hit_rate": 0.30,
                "cost_per_task": 0.05,
                ...
            }
        """
        if not task_records:
            return {
                "tokens_per_task": 0,
                "token_efficiency_score": 0.0,
                "cache_hit_rate": 0.0,
                "cost_per_task": 0.0
            }
        
        tokens_list = [t.get("tokens_used", 0) for t in task_records if t.get("tokens_used")]
        avg_tokens = statistics.mean(tokens_list) if tokens_list else 0
        
        # Token 效率得分 (假设 2000 tokens 为基准)
        baseline = baseline_avg_tokens or 2000
        token_efficiency = max(1.0 - (avg_tokens / (baseline * 2)), 0)
        
        # 缓存命中率 (如果有缓存数据)
        cache_hits = sum(1 for t in task_records if t.get("metadata", {}).get("cache_hit", False))
        cache_hit_rate = cache_hits / max(len(task_records), 1)
        
        # 估算成本 (假设 $0.002 per 1K tokens)
        cost_per_task = (avg_tokens / 1000) * 0.002
        
        return {
            "tokens_per_task": round(avg_tokens, 2),
            "token_efficiency_score": round(token_efficiency, 4),
            "cache_hit_rate": round(cache_hit_rate, 4),
            "cost_per_task": round(cost_per_task, 4),
            "total_cost": round(cost_per_task * len(task_records), 4)
        }
    
    @staticmethod
    def calculate_skill_metrics(
        skill_id: str,
        task_records: List[Dict]
    ) -> Dict[str, Any]:
        """
        计算特定 Skill 的指标
        
        Args:
            skill_id: Skill ID
            task_records: 包含该 Skill 的任务记录
        
        Returns:
            {
                "skill_id": "code_review",
                "usage_count": 156,
                "success_rate": 0.92,
                "avg_duration": 45.2,
                "avg_rating": 4.5,
                "reuse_rate": 0.75,
                ...
            }
        """
        # 过滤出使用该 Skill 的任务
        skill_tasks = [
            t for t in task_records
            if skill_id in t.get("skills_used", [])
        ]
        
        basic_metrics = MetricsCalculator.calculate_basic_metrics(skill_tasks)
        
        # 复用率 (同一用户多次使用)
        user_usage = {}
        for t in skill_tasks:
            user_id = t.get("user_id", "anonymous")
            user_usage[user_id] = user_usage.get(user_id, 0) + 1
        
        repeat_users = sum(1 for count in user_usage.values() if count > 1)
        total_users = len(user_usage)
        reuse_rate = repeat_users / max(total_users, 1)
        
        return {
            "skill_id": skill_id,
            "usage_count": basic_metrics["total_tasks"],
            "success_rate": basic_metrics["success_rate"],
            "avg_duration": basic_metrics["avg_duration"],
            "avg_tokens": basic_metrics["avg_tokens"],
            "reuse_rate": round(reuse_rate, 4),
            "unique_users": total_users,
            "avg_usage_per_user": round(sum(user_usage.values()) / max(total_users, 1), 2)
        }
    
    @staticmethod
    def generate_summary_report(
        task_records: List[Dict],
        feedback_records: List[Dict],
        period_days: int = 7
    ) -> Dict[str, Any]:
        """
        生成综合摘要报告
        
        Args:
            task_records: 任务记录
            feedback_records: 反馈记录
            period_days: 统计周期
        
        Returns:
            完整的指标报告
        """
        basic = MetricsCalculator.calculate_basic_metrics(task_records)
        quality = MetricsCalculator.calculate_quality_metrics(task_records, feedback_records)
        efficiency = MetricsCalculator.calculate_efficiency_metrics(task_records)
        
        return {
            "period_days": period_days,
            "generated_at": datetime.now().isoformat(),
            "basic_metrics": basic,
            "quality_metrics": quality,
            "efficiency_metrics": efficiency,
            "health_score": MetricsCalculator._calculate_health_score(
                basic, quality, efficiency
            )
        }
    
    @staticmethod
    def _calculate_health_score(
        basic: Dict,
        quality: Dict,
        efficiency: Dict
    ) -> float:
        """
        计算系统健康度评分 (0-100)
        
        权重:
        - 成功率: 30%
        - 用户满意度: 30%
        - 效率: 20%
        - 稳定性: 20%
        """
        # 成功率得分 (0-100)
        success_score = basic.get("success_rate", 0) * 100
        
        # 满意度得分 (0-100)
        satisfaction_score = (quality.get("avg_rating", 0) / 5) * 100
        
        # 效率得分 (0-100)
        efficiency_score = efficiency.get("token_efficiency_score", 0) * 100
        
        # 稳定性得分 (基于标准差，越低越稳定)
        std_duration = basic.get("std_duration", 0)
        avg_duration = basic.get("avg_duration", 1)
        cv = std_duration / max(avg_duration, 1)  # 变异系数
        stability_score = max(100 - (cv * 100), 0)
        
        # 加权计算
        health_score = (
            success_score * 0.3 +
            satisfaction_score * 0.3 +
            efficiency_score * 0.2 +
            stability_score * 0.2
        )
        
        return round(min(max(health_score, 0), 100), 2)
