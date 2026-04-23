"""
A/B 测试框架

实现流量的随机分配、数据收集和统计显著性检验
"""

import uuid
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from scipy import stats
import numpy as np

from user_scoring.database import DatabaseManager


class ABTestFramework:
    """
    A/B 测试框架
    
    工作流程:
    1. 创建新版本时，同时保留旧版本
    2. 将用户请求随机分配到 A/B 两组
    3. 收集两组的性能数据
    4. 统计显著性检验
    5. 做出保留/回退决策
    """
    
    def __init__(self, db_path: str = None):
        self.db = DatabaseManager(db_path)
        self.db.connect()
        
        # 默认配置
        self.default_config = {
            "traffic_split": 0.5,  # 50/50 分配
            "min_sample_size": 100,  # 最小样本量
            "confidence_level": 0.95,  # 置信水平 95%
            "statistical_power": 0.8,  # 统计功效 80%
            "test_duration_days": 7  # 测试持续时间
        }
    
    async def start_ab_test(
        self,
        test_id: str = None,
        version_a: str = "baseline",
        version_b: str = None,
        traffic_split: float = 0.5,
        duration_days: int = 7,
        metrics_to_track: List[str] = None
    ) -> Dict[str, Any]:
        """
        启动 A/B 测试
        
        Args:
            test_id: 测试 ID (可选，自动生成)
            version_a: 基线版本
            version_b: 新版本
            traffic_split: A/B 流量分配比例 (0.5 = 50/50)
            duration_days: 测试持续时间（天）
            metrics_to_track: 要追踪的指标列表
        
        Returns:
            测试配置信息
        """
        if not test_id:
            test_id = f"ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        config = {
            "test_id": test_id,
            "version_a": version_a,
            "version_b": version_b or f"candidate_{datetime.now().strftime('%Y%m%d')}",
            "traffic_split": traffic_split,
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(days=duration_days)).isoformat(),
            "duration_days": duration_days,
            "status": "running",
            "metrics_to_track": metrics_to_track or [
                "success_rate",
                "avg_duration",
                "avg_tokens",
                "user_rating"
            ]
        }
        
        # 保存测试配置到数据库
        self.db.execute("""
            INSERT INTO ab_test_assignments (test_id, user_id, variant)
            VALUES (?, ?, ?)
        """, (test_id, "__config__", "initialized"))
        
        print(f"✅ A/B Test started: {test_id}")
        print(f"   Version A (Baseline): {version_a}")
        print(f"   Version B (Candidate): {config['version_b']}")
        print(f"   Traffic Split: {traffic_split*100:.0f}% / {(1-traffic_split)*100:.0f}%")
        print(f"   Duration: {duration_days} days")
        
        return config
    
    async def route_request(self, user_id: str, test_id: str) -> str:
        """
        根据用户 ID 路由到 A 或 B 版本
        
        Args:
            user_id: 用户 ID
            test_id: 测试 ID
        
        Returns:
            'A' 或 'B'
        """
        # 检查是否已有分配
        existing = self.db.fetchone(
            "SELECT variant FROM ab_test_assignments WHERE test_id = ? AND user_id = ?",
            (test_id, user_id)
        )
        
        if existing:
            return existing["variant"]
        
        # 获取测试配置
        config = self.db.fetchone(
            "SELECT * FROM ab_test_assignments WHERE test_id = ? AND user_id = '__config__'",
            (test_id,)
        )
        
        if not config:
            raise ValueError(f"Test {test_id} not found")
        
        traffic_split = 0.5  # 默认 50/50
        
        # 使用一致性哈希确保同一用户总是分配到同一组
        hash_value = int(hashlib.md5(f"{test_id}:{user_id}".encode()).hexdigest(), 16)
        normalized = (hash_value % 10000) / 10000.0
        
        variant = "A" if normalized < traffic_split else "B"
        
        # 记录分配
        self.db.execute("""
            INSERT INTO ab_test_assignments (test_id, user_id, variant)
            VALUES (?, ?, ?)
        """, (test_id, user_id, variant))
        
        return variant
    
    async def evaluate_test(self, test_id: str) -> Dict[str, Any]:
        """
        评估 A/B 测试结果
        
        Args:
            test_id: 测试 ID
        
        Returns:
            评估结果，包含统计显著性检验
        """
        # 获取测试配置
        config = self.db.fetchone(
            "SELECT * FROM ab_test_assignments WHERE test_id = ? AND user_id = '__config__'",
            (test_id,)
        )
        
        if not config:
            raise ValueError(f"Test {test_id} not found")
        
        # 获取 A 组和 B 组的用户
        group_a_users = self.db.fetchall(
            "SELECT user_id FROM ab_test_assignments WHERE test_id = ? AND variant = 'A'",
            (test_id,)
        )
        group_b_users = self.db.fetchall(
            "SELECT user_id FROM ab_test_assignments WHERE test_id = ? AND variant = 'B'",
            (test_id,)
        )
        
        a_user_ids = [u["user_id"] for u in group_a_users if u["user_id"] != "__config__"]
        b_user_ids = [u["user_id"] for u in group_b_users if u["user_id"] != "__config__"]
        
        # 获取两组的指标
        metrics_a = self._calculate_group_metrics(a_user_ids)
        metrics_b = self._calculate_group_metrics(b_user_ids)
        
        # 统计显著性检验
        statistical_results = {}
        
        # 1. 成功率对比 (Z-test)
        if metrics_a["total_tasks"] > 0 and metrics_b["total_tasks"] > 0:
            success_test = self._z_test_proportions(
                metrics_a["success_count"], metrics_a["total_tasks"],
                metrics_b["success_count"], metrics_b["total_tasks"]
            )
            statistical_results["success_rate"] = success_test
        
        # 2. 平均耗时对比 (t-test)
        if metrics_a.get("durations") and metrics_b.get("durations"):
            duration_test = self._t_test_independent(
                metrics_a["durations"],
                metrics_b["durations"]
            )
            statistical_results["duration"] = duration_test
        
        # 3. 用户评分对比 (t-test)
        if metrics_a.get("ratings") and metrics_b.get("ratings"):
            rating_test = self._t_test_independent(
                metrics_a["ratings"],
                metrics_b["ratings"]
            )
            statistical_results["rating"] = rating_test
        
        # 综合决策
        decision = self._make_decision(statistical_results, metrics_a, metrics_b)
        
        result = {
            "test_id": test_id,
            "status": "completed",
            "group_a_metrics": {k: v for k, v in metrics_a.items() if k != "durations" and k != "ratings"},
            "group_b_metrics": {k: v for k, v in metrics_b.items() if k != "durations" and k != "ratings"},
            "statistical_tests": statistical_results,
            "decision": decision,
            "sample_sizes": {
                "group_a": len(a_user_ids),
                "group_b": len(b_user_ids)
            },
            "evaluated_at": datetime.now().isoformat()
        }
        
        return result
    
    def _calculate_group_metrics(self, user_ids: List[str]) -> Dict[str, Any]:
        """计算一组用户的指标"""
        if not user_ids:
            return {
                "total_tasks": 0,
                "success_count": 0,
                "success_rate": 0,
                "durations": [],
                "ratings": []
            }
        
        placeholders = ",".join(["?"] * len(user_ids))
        
        # 获取任务数据
        tasks = self.db.fetchall(f"""
            SELECT * FROM task_executions 
            WHERE user_id IN ({placeholders})
        """, user_ids)
        
        total_tasks = len(tasks)
        success_count = sum(1 for t in tasks if t["status"] == "success")
        durations = [t["duration_seconds"] for t in tasks if t["duration_seconds"]]
        
        # 获取评分
        task_ids = [t["task_id"] for t in tasks]
        if task_ids:
            placeholders_tasks = ",".join(["?"] * len(task_ids))
            feedbacks = self.db.fetchall(f"""
                SELECT rating FROM user_feedbacks 
                WHERE task_id IN ({placeholders_tasks})
            """, task_ids)
            ratings = [f["rating"] for f in feedbacks]
        else:
            ratings = []
        
        return {
            "total_tasks": total_tasks,
            "success_count": success_count,
            "success_rate": success_count / max(total_tasks, 1),
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "avg_rating": sum(ratings) / len(ratings) if ratings else 0,
            "durations": durations,
            "ratings": ratings
        }
    
    def _z_test_proportions(
        self,
        successes_a: int, n_a: int,
        successes_b: int, n_b: int
    ) -> Dict[str, float]:
        """
        两个比例的 Z 检验
        
        Returns:
            {
                "z_statistic": ...,
                "p_value": ...,
                "significant": True/False,
                "improvement": ...%
            }
        """
        p_a = successes_a / max(n_a, 1)
        p_b = successes_b / max(n_b, 1)
        
        # 合并比例
        p_pool = (successes_a + successes_b) / max(n_a + n_b, 1)
        
        # 标准误
        se = np.sqrt(p_pool * (1 - p_pool) * (1/max(n_a, 1) + 1/max(n_b, 1)))
        
        if se == 0:
            return {
                "z_statistic": 0,
                "p_value": 1.0,
                "significant": False,
                "improvement": 0
            }
        
        # Z 统计量
        z = (p_b - p_a) / se
        
        # P 值 (双尾检验)
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        
        # 改进百分比
        improvement = ((p_b - p_a) / max(p_a, 0.001)) * 100
        
        return {
            "z_statistic": round(z, 4),
            "p_value": round(p_value, 4),
            "significant": p_value < 0.05,
            "improvement": round(improvement, 2)
        }
    
    def _t_test_independent(
        self,
        sample_a: List[float],
        sample_b: List[float]
    ) -> Dict[str, float]:
        """
        独立样本 t 检验
        
        Returns:
            {
                "t_statistic": ...,
                "p_value": ...,
                "significant": True/False,
                "mean_difference": ...
            }
        """
        if len(sample_a) < 2 or len(sample_b) < 2:
            return {
                "t_statistic": 0,
                "p_value": 1.0,
                "significant": False,
                "mean_difference": 0
            }
        
        t_stat, p_value = stats.ttest_ind(sample_a, sample_b)
        
        mean_diff = np.mean(sample_b) - np.mean(sample_a)
        
        return {
            "t_statistic": round(t_stat, 4),
            "p_value": round(p_value, 4),
            "significant": p_value < 0.05,
            "mean_difference": round(mean_diff, 4)
        }
    
    def _make_decision(
        self,
        statistical_results: Dict,
        metrics_a: Dict,
        metrics_b: Dict
    ) -> Dict[str, Any]:
        """
        基于统计检验结果做决策
        
        Returns:
            {
                "action": "KEEP_AND_PROMOTE" | "KEEP" | "ROLLBACK",
                "reason": "...",
                "confidence": 0.95
            }
        """
        # 检查是否有显著改进
        significant_improvements = 0
        total_tests = len(statistical_results)
        
        for metric, result in statistical_results.items():
            if result.get("significant") and result.get("improvement", 0) > 0:
                significant_improvements += 1
        
        # 决策逻辑
        if total_tests == 0:
            return {
                "action": "REVIEW",
                "reason": "Insufficient data for decision",
                "confidence": 0
            }
        
        improvement_ratio = significant_improvements / total_tests
        
        if improvement_ratio >= 0.6:
            # 大部分指标显著改进
            return {
                "action": "KEEP_AND_PROMOTE",
                "reason": f"{significant_improvements}/{total_tests} metrics significantly improved",
                "confidence": 0.95
            }
        elif improvement_ratio >= 0.3:
            # 部分指标改进
            return {
                "action": "KEEP",
                "reason": f"{significant_improvements}/{total_tests} metrics improved",
                "confidence": 0.80
            }
        else:
            # 无明显改进或退化
            return {
                "action": "ROLLBACK",
                "reason": f"Only {significant_improvements}/{total_tests} metrics improved",
                "confidence": 0.85
            }
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


if __name__ == "__main__":
    # 测试 A/B 测试框架
    import asyncio
    
    async def test_ab_framework():
        framework = ABTestFramework(":memory:")
        
        # 启动测试
        config = await framework.start_ab_test(
            test_id="test_001",
            version_a="v1.0",
            version_b="v2.0",
            duration_days=7
        )
        
        # 模拟用户分配
        for i in range(100):
            variant = await framework.route_request(f"user_{i}", "test_001")
            print(f"User {i} -> Variant {variant}")
        
        # 评估测试
        result = await framework.evaluate_test("test_001")
        print("\nA/B Test Result:")
        print(f"Decision: {result['decision']['action']}")
        print(f"Reason: {result['decision']['reason']}")
        
        framework.close()
    
    asyncio.run(test_ab_framework())
