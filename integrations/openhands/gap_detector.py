"""
OpenHands 能力缺口检测器

基于执行历史和用户反馈，自动检测能力缺口
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import json


class GapDetector:
    """
    能力缺口检测器
    
    检测的缺口类型:
    - 功能缺失 (missing_feature)
    - 性能瓶颈 (performance_bottleneck)
    - 错误模式 (error_pattern)
    - 用户痛点 (user_pain_point)
    """
    
    def __init__(self, behavior_tracker=None):
        self.tracker = behavior_tracker
        self.detected_gaps: List[Dict] = []
    
    def detect_gaps_from_execution_history(
        self,
        task_records: List[Dict],
        threshold_success_rate: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        从执行历史中检测缺口
        
        Args:
            task_records: 任务执行记录列表
            threshold_success_rate: 成功率阈值
        
        Returns:
            检测到的缺口列表
        """
        gaps = []
        
        # 1. 按任务类型分组分析
        task_types = self._group_by_task_type(task_records)
        
        for task_type, records in task_types.items():
            total = len(records)
            success_count = sum(1 for r in records if r.get("status") == "success")
            success_rate = success_count / max(total, 1)
            
            # 检测低成功率的任务类型
            if success_rate < threshold_success_rate and total >= 5:
                gaps.append({
                    "type": "low_success_rate",
                    "category": task_type,
                    "severity": "high" if success_rate < 0.6 else "medium",
                    "success_rate": round(success_rate, 4),
                    "total_tasks": total,
                    "description": f"Task type '{task_type}' has low success rate: {success_rate*100:.1f}%",
                    "detected_at": datetime.now().isoformat()
                })
        
        # 2. 检测常见错误模式
        error_patterns = self._analyze_error_patterns(task_records)
        gaps.extend(error_patterns)
        
        # 3. 检测性能瓶颈
        performance_issues = self._detect_performance_bottlenecks(task_records)
        gaps.extend(performance_issues)
        
        # 缓存结果
        self.detected_gaps = gaps
        
        return gaps
    
    def detect_gaps_from_user_feedback(
        self,
        feedback_records: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        从用户反馈中检测缺口
        
        Args:
            feedback_records: 用户反馈记录
        
        Returns:
            检测到的缺口列表
        """
        gaps = []
        
        # 分析低评分反馈
        low_ratings = [f for f in feedback_records if f.get("rating", 5) <= 2]
        
        if low_ratings:
            # 提取常见问题
            common_issues = self._extract_common_issues(low_ratings)
            
            for issue in common_issues:
                gaps.append({
                    "type": "user_pain_point",
                    "issue": issue["topic"],
                    "severity": "high" if issue["count"] >= 5 else "medium",
                    "occurrence_count": issue["count"],
                    "description": f"Users frequently complain about: {issue['topic']}",
                    "detected_at": datetime.now().isoformat()
                })
        
        return gaps
    
    def detect_missing_features(
        self,
        failed_tasks: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        从失败任务中检测缺失功能
        
        Args:
            failed_tasks: 失败的任务记录
        
        Returns:
            缺失功能列表
        """
        gaps = []
        
        # 分析失败原因
        failure_reasons = {}
        for task in failed_tasks:
            error_msg = task.get("error_message", "").lower()
            
            # 提取关键词
            keywords = self._extract_failure_keywords(error_msg)
            for keyword in keywords:
                failure_reasons[keyword] = failure_reasons.get(keyword, 0) + 1
        
        # 识别频繁出现的失败原因（可能是缺失功能）
        for reason, count in failure_reasons.items():
            if count >= 3:  # 至少出现 3 次
                gaps.append({
                    "type": "missing_feature",
                    "feature": reason,
                    "severity": "high" if count >= 10 else "medium",
                    "occurrence_count": count,
                    "description": f"Missing feature: {reason} (failed {count} times)",
                    "detected_at": datetime.now().isoformat()
                })
        
        return gaps
    
    def _group_by_task_type(self, task_records: List[Dict]) -> Dict[str, List]:
        """按任务类型分组"""
        groups = {}
        for record in task_records:
            task_type = record.get("task_type", "unknown")
            if task_type not in groups:
                groups[task_type] = []
            groups[task_type].append(record)
        return groups
    
    def _analyze_error_patterns(self, task_records: List[Dict]) -> List[Dict]:
        """分析错误模式"""
        gaps = []
        
        # 统计错误类型
        error_types = {}
        for record in task_records:
            if record.get("status") == "failed":
                error_msg = record.get("error_message", "unknown")
                error_type = self._classify_error(error_msg)
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # 识别频繁错误
        for error_type, count in error_types.items():
            if count >= 5:
                gaps.append({
                    "type": "error_pattern",
                    "error_type": error_type,
                    "severity": "high" if count >= 10 else "medium",
                    "occurrence_count": count,
                    "description": f"Frequent error pattern: {error_type} ({count} occurrences)",
                    "detected_at": datetime.now().isoformat()
                })
        
        return gaps
    
    def _detect_performance_bottlenecks(
        self,
        task_records: List[Dict]
    ) -> List[Dict]:
        """检测性能瓶颈"""
        gaps = []
        
        # 计算平均耗时
        durations = [r.get("duration_seconds", 0) for r in task_records if r.get("duration_seconds")]
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            
            # 检测超时任务
            timeout_count = sum(1 for d in durations if d > 120)  # 超过 2 分钟
            
            if timeout_count >= 3:
                gaps.append({
                    "type": "performance_bottleneck",
                    "metric": "timeout_rate",
                    "severity": "high",
                    "timeout_count": timeout_count,
                    "avg_duration": round(avg_duration, 2),
                    "description": f"High timeout rate: {timeout_count} tasks exceeded 120s",
                    "detected_at": datetime.now().isoformat()
                })
            
            # 检测慢任务
            slow_count = sum(1 for d in durations if d > 60)
            if slow_count >= len(durations) * 0.3:  # 30% 以上任务慢
                gaps.append({
                    "type": "performance_bottleneck",
                    "metric": "slow_tasks",
                    "severity": "medium",
                    "slow_count": slow_count,
                    "percentage": round(slow_count / len(durations) * 100, 2),
                    "description": f"{slow_count}/{len(durations)} tasks are slow (>60s)",
                    "detected_at": datetime.now().isoformat()
                })
        
        return gaps
    
    def _extract_common_issues(self, low_ratings: List[Dict]) -> List[Dict]:
        """提取常见问题"""
        # 简单实现：基于评论关键词
        issue_counts = {}
        
        for feedback in low_ratings:
            comment = feedback.get("comment", "").lower()
            
            # 检查常见关键词
            keywords = ["slow", "error", "fail", "confusing", "difficult", "not work"]
            for keyword in keywords:
                if keyword in comment:
                    issue_counts[keyword] = issue_counts.get(keyword, 0) + 1
        
        return [
            {"topic": topic, "count": count}
            for topic, count in issue_counts.items()
            if count >= 2
        ]
    
    def _extract_failure_keywords(self, error_msg: str) -> List[str]:
        """从错误消息中提取关键词"""
        keywords = []
        
        # 常见失败原因关键词
        common_keywords = [
            "typescript", "docker", "api", "authentication",
            "timeout", "memory", "permission", "dependency"
        ]
        
        for keyword in common_keywords:
            if keyword in error_msg.lower():
                keywords.append(keyword)
        
        return keywords
    
    def _classify_error(self, error_msg: str) -> str:
        """分类错误类型"""
        error_lower = error_msg.lower()
        
        if "timeout" in error_lower:
            return "timeout"
        elif "permission" in error_lower or "access denied" in error_lower:
            return "permission_error"
        elif "not found" in error_lower or "404" in error_lower:
            return "not_found"
        elif "memory" in error_lower:
            return "memory_error"
        elif "syntax" in error_lower:
            return "syntax_error"
        else:
            return "other"
    
    def get_detected_gaps(self) -> List[Dict]:
        """获取检测到的缺口"""
        return self.detected_gaps
    
    def generate_gap_report(self) -> Dict[str, Any]:
        """生成缺口报告"""
        gaps = self.detected_gaps
        
        # 按严重程度分组
        high_severity = [g for g in gaps if g.get("severity") == "high"]
        medium_severity = [g for g in gaps if g.get("severity") == "medium"]
        
        return {
            "total_gaps": len(gaps),
            "high_severity_count": len(high_severity),
            "medium_severity_count": len(medium_severity),
            "gaps": gaps,
            "top_priorities": high_severity[:5],  # 前 5 个高优先级
            "generated_at": datetime.now().isoformat()
        }
