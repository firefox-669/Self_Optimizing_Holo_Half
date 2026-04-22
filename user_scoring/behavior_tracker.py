"""
用户行为追踪器

采集用户在 OpenHands/OpenSpace 中的行为数据
包括任务执行、用户反馈、Skill 使用等
"""

import uuid
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from .database import DatabaseManager


class UserBehaviorTracker:
    """
    用户行为追踪器
    
    采集的数据:
    - 任务执行记录 (task_id, duration, tokens, success/fail)
    - 用户反馈 (显式评分 1-5星，隐式行为推断)
    - Skill 使用频率和效果
    - 错误与重试次数
    """
    
    def __init__(self, db_path: str = None):
        self.db = DatabaseManager(db_path)
        self.db.connect()
    
    def record_task_execution(self, execution_data: Dict[str, Any]) -> str:
        """
        记录任务执行
        
        Args:
            execution_data: {
                "task_id": "xxx",  # 可选，不传则自动生成
                "user_id": "user_123",
                "mode": "normal" | "evolution",
                "task_type": "openhands" | "openspace",
                "instruction": "任务描述",
                "status": "success" | "failed" | "timeout",
                "start_time": "2026-04-21T10:00:00",
                "end_time": "2026-04-21T10:01:30",
                "duration_seconds": 90.5,
                "tokens_used": 1234,
                "error_message": "...",  # 可选
                "skills_used": ["skill_1", "skill_2"],  # 可选
                "metadata": {...}  # 可选
            }
        
        Returns:
            task_id
        """
        task_id = execution_data.get("task_id") or f"task_{uuid.uuid4().hex[:12]}"
        
        # 序列化列表和字典为 JSON
        skills_used = json.dumps(execution_data.get("skills_used", []))
        metadata = json.dumps(execution_data.get("metadata", {}))
        
        query = """
            INSERT OR REPLACE INTO task_executions 
            (task_id, user_id, mode, task_type, instruction, status, 
             start_time, end_time, duration_seconds, tokens_used, 
             error_message, skills_used, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            task_id,
            execution_data.get("user_id"),
            execution_data["mode"],
            execution_data.get("task_type"),
            execution_data.get("instruction"),
            execution_data["status"],
            execution_data.get("start_time"),
            execution_data.get("end_time"),
            execution_data.get("duration_seconds"),
            execution_data.get("tokens_used"),
            execution_data.get("error_message"),
            skills_used,
            metadata
        )
        
        self.db.execute(query, params)
        
        # 更新 Skill 使用统计
        if execution_data.get("skills_used"):
            self._update_skill_stats(execution_data)
        
        return task_id
    
    def record_user_feedback(
        self, 
        task_id: str, 
        rating: int,
        user_id: str = None,
        feedback_type: str = "explicit",
        comment: str = None
    ):
        """
        记录用户显式反馈
        
        Args:
            task_id: 任务 ID
            rating: 1-5 星评分
            user_id: 用户 ID
            feedback_type: 'explicit' (显式) 或 'implicit' (隐式)
            comment: 可选评论
        """
        if not (1 <= rating <= 5):
            raise ValueError(f"Rating must be between 1 and 5, got {rating}")
        
        query = """
            INSERT INTO user_feedbacks (task_id, user_id, rating, feedback_type, comment)
            VALUES (?, ?, ?, ?, ?)
        """
        
        self.db.execute(query, (task_id, user_id, rating, feedback_type, comment))
    
    def infer_implicit_feedback(self, task_id: str) -> Optional[int]:
        """
        根据用户行为推断隐式反馈
        
        规则:
        - 任务成功 + 无重试 → 5星
        - 任务成功 + 1次重试 → 4星
        - 任务成功 + 多次重试 → 3星
        - 任务失败 → 2星
        - 任务超时/错误 → 1星
        
        Returns:
            推断的评分 (1-5)，如果无法推断则返回 None
        """
        task = self.db.fetchone(
            "SELECT * FROM task_executions WHERE task_id = ?",
            (task_id,)
        )
        
        if not task:
            return None
        
        status = task["status"]
        metadata = json.loads(task.get("metadata") or "{}")
        retry_count = metadata.get("retry_count", 0)
        
        if status == "success":
            if retry_count == 0:
                return 5
            elif retry_count == 1:
                return 4
            else:
                return 3
        elif status == "failed":
            return 2
        else:  # timeout or other errors
            return 1
    
    def get_task_metrics(self, task_id: str) -> Optional[Dict]:
        """获取单个任务的完整指标"""
        task = self.db.fetchone(
            "SELECT * FROM task_executions WHERE task_id = ?",
            (task_id,)
        )
        
        if not task:
            return None
        
        # 解析 JSON 字段
        task["skills_used"] = json.loads(task.get("skills_used") or "[]")
        task["metadata"] = json.loads(task.get("metadata") or "{}")
        
        # 获取用户反馈
        feedback = self.db.fetchone(
            "SELECT * FROM user_feedbacks WHERE task_id = ? ORDER BY created_at DESC LIMIT 1",
            (task_id,)
        )
        
        task["user_feedback"] = dict(feedback) if feedback else None
        
        return task
    
    def get_user_tasks(
        self, 
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """获取用户的任务历史"""
        query = """
            SELECT * FROM task_executions 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        
        tasks = self.db.fetchall(query, (user_id, limit, offset))
        
        # 解析 JSON 字段
        for task in tasks:
            task["skills_used"] = json.loads(task.get("skills_used") or "[]")
            task["metadata"] = json.loads(task.get("metadata") or "{}")
        
        return tasks
    
    def get_version_metrics(
        self, 
        version_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        获取某个版本的性能指标
        
        Args:
            version_id: 版本 ID
            days: 统计天数
        
        Returns:
            {
                "total_tasks": 156,
                "success_rate": 0.92,
                "avg_duration": 45.2,
                "avg_tokens": 1234,
                "avg_rating": 4.5,
                ...
            }
        """
        # 获取该版本的任务
        tasks = self.db.fetchall("""
            SELECT te.* 
            FROM task_executions te
            JOIN version_logs vl ON te.metadata LIKE ?
            WHERE vl.version_id = ?
            AND te.created_at >= datetime('now', '-' || ? || ' days')
        """, (f'%version_id":"{version_id}"%', version_id, days))
        
        if not tasks:
            return {
                "total_tasks": 0,
                "success_rate": 0,
                "avg_duration": 0,
                "avg_tokens": 0,
                "avg_rating": 0
            }
        
        # 计算指标
        total = len(tasks)
        success_count = sum(1 for t in tasks if t["status"] == "success")
        durations = [t["duration_seconds"] for t in tasks if t["duration_seconds"]]
        tokens = [t["tokens_used"] for t in tasks if t["tokens_used"]]
        
        # 获取评分
        task_ids = [t["task_id"] for t in tasks]
        placeholders = ",".join(["?"] * len(task_ids))
        feedbacks = self.db.fetchall(f"""
            SELECT rating FROM user_feedbacks 
            WHERE task_id IN ({placeholders})
        """, task_ids)
        
        ratings = [f["rating"] for f in feedbacks]
        
        return {
            "total_tasks": total,
            "success_count": success_count,
            "fail_count": total - success_count,
            "success_rate": success_count / total if total > 0 else 0,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "avg_tokens": sum(tokens) / len(tokens) if tokens else 0,
            "avg_rating": sum(ratings) / len(ratings) if ratings else 0,
            "total_tokens": sum(tokens) if tokens else 0
        }
    
    def _update_skill_stats(self, execution_data: Dict):
        """更新 Skill 使用统计"""
        skills_used = execution_data.get("skills_used", [])
        
        for skill_id in skills_used:
            # 检查是否已有统计
            existing = self.db.fetchone(
                "SELECT * FROM skill_usage_stats WHERE skill_id = ?",
                (skill_id,)
            )
            
            if existing:
                # 更新现有统计
                new_count = existing["execution_count"] + 1
                new_success = existing["success_count"] + (1 if execution_data["status"] == "success" else 0)
                new_fail = existing["fail_count"] + (1 if execution_data["status"] == "failed" else 0)
                
                # 重新计算平均值
                avg_duration = (
                    (existing["avg_duration"] * existing["execution_count"] + 
                     execution_data.get("duration_seconds", 0)) / new_count
                )
                avg_tokens = (
                    (existing["avg_tokens"] * existing["execution_count"] + 
                     execution_data.get("tokens_used", 0)) / new_count
                )
                
                query = """
                    UPDATE skill_usage_stats 
                    SET execution_count = ?,
                        success_count = ?,
                        fail_count = ?,
                        avg_duration = ?,
                        avg_tokens = ?,
                        last_used_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE skill_id = ?
                """
                
                self.db.execute(query, (
                    new_count, new_success, new_fail,
                    avg_duration, avg_tokens, skill_id
                ))
            else:
                # 创建新统计
                query = """
                    INSERT INTO skill_usage_stats 
                    (skill_id, execution_count, success_count, fail_count,
                     avg_duration, avg_tokens, last_used_at)
                    VALUES (?, 1, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """
                
                self.db.execute(query, (
                    skill_id,
                    1 if execution_data["status"] == "success" else 0,
                    1 if execution_data["status"] == "failed" else 0,
                    execution_data.get("duration_seconds", 0),
                    execution_data.get("tokens_used", 0)
                ))
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
