"""
OpenHands 性能监控器

实时监控 OpenHands 的执行性能，检测异常和瓶颈
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import statistics


class PerformanceMonitor:
    """
    性能监控器
    
    监控指标:
    - 响应时间
    - Token 消耗
    - 成功率
    - 资源使用率
    - 错误率
    """
    
    def __init__(self):
        self.metrics_history: List[Dict] = []
        self.alerts: List[Dict] = []
        
        # 阈值配置
        self.thresholds = {
            "max_duration": 120,  # 最大耗时（秒）
            "max_tokens": 5000,   # 最大 Token 消耗
            "min_success_rate": 0.8,  # 最低成功率
            "max_error_rate": 0.2,    # 最高错误率
            "alert_window_minutes": 30  # 告警时间窗口
        }
    
    def record_execution(self, execution_data: Dict[str, Any]):
        """
        记录执行数据
        
        Args:
            execution_data: {
                "task_id": "...",
                "duration": 45.2,
                "tokens_used": 1234,
                "success": True,
                "error": None,
                "timestamp": "..."
            }
        """
        record = {
            "task_id": execution_data.get("task_id"),
            "duration": execution_data.get("duration_seconds", 0),
            "tokens_used": execution_data.get("tokens_used", 0),
            "success": execution_data.get("status") == "success",
            "error": execution_data.get("error_message"),
            "timestamp": datetime.now().isoformat()
        }
        
        self.metrics_history.append(record)
        
        # 检查是否触发告警
        self._check_alerts(record)
    
    def get_current_metrics(self, window_minutes: int = 30) -> Dict[str, Any]:
        """
        获取当前性能指标（指定时间窗口内）
        
        Args:
            window_minutes: 时间窗口（分钟）
        
        Returns:
            当前性能指标
        """
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        
        # 过滤时间窗口内的记录
        recent_records = [
            r for r in self.metrics_history
            if datetime.fromisoformat(r["timestamp"]) >= cutoff_time
        ]
        
        if not recent_records:
            return {
                "total_executions": 0,
                "success_rate": 0,
                "avg_duration": 0,
                "avg_tokens": 0,
                "error_rate": 0,
                "p95_duration": 0,
                "period_minutes": window_minutes
            }
        
        # 计算指标
        total = len(recent_records)
        success_count = sum(1 for r in recent_records if r["success"])
        durations = [r["duration"] for r in recent_records if r["duration"] > 0]
        tokens = [r["tokens_used"] for r in recent_records if r["tokens_used"] > 0]
        error_count = sum(1 for r in recent_records if r["error"])
        
        return {
            "total_executions": total,
            "success_count": success_count,
            "fail_count": total - success_count,
            "success_rate": round(success_count / max(total, 1), 4),
            "avg_duration": round(statistics.mean(durations), 2) if durations else 0,
            "median_duration": round(statistics.median(durations), 2) if durations else 0,
            "p95_duration": round(sorted(durations)[int(len(durations) * 0.95)], 2) if durations else 0,
            "avg_tokens": round(statistics.mean(tokens), 2) if tokens else 0,
            "total_tokens": sum(tokens),
            "error_count": error_count,
            "error_rate": round(error_count / max(total, 1), 4),
            "period_minutes": window_minutes,
            "calculated_at": datetime.now().isoformat()
        }
    
    def detect_anomalies(self, window_minutes: int = 60) -> List[Dict[str, Any]]:
        """
        检测性能异常
        
        Args:
            window_minutes: 检测时间窗口
        
        Returns:
            异常列表
        """
        anomalies = []
        
        metrics = self.get_current_metrics(window_minutes)
        
        if metrics["total_executions"] == 0:
            return anomalies
        
        # 1. 检测高错误率
        if metrics["error_rate"] > self.thresholds["max_error_rate"]:
            anomalies.append({
                "type": "high_error_rate",
                "severity": "high",
                "current_value": metrics["error_rate"],
                "threshold": self.thresholds["max_error_rate"],
                "description": f"Error rate is {metrics['error_rate']*100:.1f}%, exceeds threshold {self.thresholds['max_error_rate']*100:.1f}%",
                "detected_at": datetime.now().isoformat()
            })
        
        # 2. 检测低成功率
        if metrics["success_rate"] < self.thresholds["min_success_rate"]:
            anomalies.append({
                "type": "low_success_rate",
                "severity": "high",
                "current_value": metrics["success_rate"],
                "threshold": self.thresholds["min_success_rate"],
                "description": f"Success rate is {metrics['success_rate']*100:.1f}%, below threshold {self.thresholds['min_success_rate']*100:.1f}%",
                "detected_at": datetime.now().isoformat()
            })
        
        # 3. 检测高耗时
        if metrics["p95_duration"] > self.thresholds["max_duration"]:
            anomalies.append({
                "type": "high_latency",
                "severity": "medium",
                "current_value": metrics["p95_duration"],
                "threshold": self.thresholds["max_duration"],
                "description": f"P95 duration is {metrics['p95_duration']:.1f}s, exceeds threshold {self.thresholds['max_duration']}s",
                "detected_at": datetime.now().isoformat()
            })
        
        # 4. 检测高 Token 消耗
        if metrics["avg_tokens"] > self.thresholds["max_tokens"]:
            anomalies.append({
                "type": "high_token_usage",
                "severity": "medium",
                "current_value": metrics["avg_tokens"],
                "threshold": self.thresholds["max_tokens"],
                "description": f"Avg token usage is {metrics['avg_tokens']:.0f}, exceeds threshold {self.thresholds['max_tokens']}",
                "detected_at": datetime.now().isoformat()
            })
        
        # 缓存告警
        self.alerts.extend(anomalies)
        
        return anomalies
    
    def get_performance_trend(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取性能趋势
        
        Args:
            hours: 回溯小时数
        
        Returns:
            趋势数据
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # 按小时分组
        hourly_metrics = {}
        
        for record in self.metrics_history:
            record_time = datetime.fromisoformat(record["timestamp"])
            if record_time < cutoff_time:
                continue
            
            hour_key = record_time.strftime("%Y-%m-%d %H:00")
            
            if hour_key not in hourly_metrics:
                hourly_metrics[hour_key] = {
                    "executions": [],
                    "durations": [],
                    "tokens": [],
                    "successes": 0,
                    "total": 0
                }
            
            hourly_metrics[hour_key]["total"] += 1
            if record["success"]:
                hourly_metrics[hour_key]["successes"] += 1
            if record["duration"] > 0:
                hourly_metrics[hour_key]["durations"].append(record["duration"])
            if record["tokens_used"] > 0:
                hourly_metrics[hour_key]["tokens"].append(record["tokens_used"])
        
        # 计算每小时的指标
        trend_data = []
        for hour_key in sorted(hourly_metrics.keys()):
            data = hourly_metrics[hour_key]
            trend_data.append({
                "hour": hour_key,
                "total_executions": data["total"],
                "success_rate": round(data["successes"] / max(data["total"], 1), 4),
                "avg_duration": round(statistics.mean(data["durations"]), 2) if data["durations"] else 0,
                "avg_tokens": round(statistics.mean(data["tokens"]), 2) if data["tokens"] else 0
            })
        
        return {
            "period_hours": hours,
            "data_points": len(trend_data),
            "trend": trend_data
        }
    
    def _check_alerts(self, record: Dict):
        """检查单条记录是否触发告警"""
        alerts = []
        
        # 检查耗时
        if record["duration"] > self.thresholds["max_duration"]:
            alerts.append({
                "type": "slow_execution",
                "task_id": record["task_id"],
                "duration": record["duration"],
                "threshold": self.thresholds["max_duration"]
            })
        
        # 检查 Token 消耗
        if record["tokens_used"] > self.thresholds["max_tokens"]:
            alerts.append({
                "type": "high_token_usage",
                "task_id": record["task_id"],
                "tokens": record["tokens_used"],
                "threshold": self.thresholds["max_tokens"]
            })
        
        # 记录告警
        if alerts:
            self.alerts.extend(alerts)
    
    def get_alerts(self, limit: int = 50) -> List[Dict]:
        """获取最近的告警"""
        return self.alerts[-limit:]
    
    def clear_old_data(self, keep_hours: int = 24):
        """清理旧数据"""
        cutoff_time = datetime.now() - timedelta(hours=keep_hours)
        
        self.metrics_history = [
            r for r in self.metrics_history
            if datetime.fromisoformat(r["timestamp"]) >= cutoff_time
        ]
        
        print(f"✅ Cleared old performance data, kept {len(self.metrics_history)} records")
    
    def generate_health_report(self) -> Dict[str, Any]:
        """生成健康度报告"""
        current = self.get_current_metrics(60)  # 最近 1 小时
        trend = self.get_performance_trend(24)  # 最近 24 小时
        anomalies = self.detect_anomalies(60)
        
        # 计算整体健康度
        health_score = self._calculate_health_score(current, anomalies)
        
        return {
            "health_score": health_score,
            "current_metrics": current,
            "trend_summary": {
                "period_hours": trend["period_hours"],
                "data_points": trend["data_points"]
            },
            "active_alerts": len(anomalies),
            "anomalies": anomalies,
            "recommendations": self._generate_recommendations(current, anomalies),
            "generated_at": datetime.now().isoformat()
        }
    
    def _calculate_health_score(
        self,
        metrics: Dict,
        anomalies: List[Dict]
    ) -> float:
        """计算健康度评分 (0-100)"""
        score = 100.0
        
        # 减去异常扣分
        for anomaly in anomalies:
            if anomaly.get("severity") == "high":
                score -= 15
            elif anomaly.get("severity") == "medium":
                score -= 10
            else:
                score -= 5
        
        # 基于成功率调整
        success_rate = metrics.get("success_rate", 1)
        if success_rate < 0.8:
            score -= 20
        elif success_rate < 0.9:
            score -= 10
        
        return round(max(min(score, 100), 0), 2)
    
    def _generate_recommendations(
        self,
        metrics: Dict,
        anomalies: List[Dict]
    ) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if metrics.get("success_rate", 1) < 0.8:
            recommendations.append("Investigate and fix frequent failures")
        
        if metrics.get("avg_duration", 0) > 60:
            recommendations.append("Optimize task execution to reduce latency")
        
        if metrics.get("avg_tokens", 0) > 3000:
            recommendations.append("Reduce token consumption through better prompting")
        
        high_severity = [a for a in anomalies if a.get("severity") == "high"]
        if high_severity:
            recommendations.append(f"Address {len(high_severity)} high-severity issues immediately")
        
        return recommendations
