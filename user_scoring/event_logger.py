"""
事件日志记录器

记录系统运行过程中的各种事件，用于审计和问题追踪
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class EventLogger:
    """
    事件日志记录器
    
    记录的事件类型:
    - TASK_STARTED: 任务开始
    - TASK_COMPLETED: 任务完成
    - TASK_FAILED: 任务失败
    - SKILL_EVOLVED: Skill 进化
    - VERSION_CREATED: 版本创建
    - AB_TEST_STARTED: A/B 测试开始
    - DECISION_MADE: 决策做出
    - ROLLBACK_EXECUTED: 执行回退
    """
    
    def __init__(self, log_dir: str = None):
        if log_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            self.log_dir = data_dir / "logs"
        else:
            self.log_dir = Path(log_dir)
        
        self.log_dir.mkdir(exist_ok=True)
        
        # 创建日志文件路径
        self.log_file = self.log_dir / f"events_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 配置 logger
        self.logger = logging.getLogger("holo_half_events")
        self.logger.setLevel(logging.INFO)
        
        # 文件 handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def log_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        level: str = "INFO"
    ):
        """
        记录事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
            level: 日志级别 (INFO, WARNING, ERROR)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        log_message = json.dumps(log_entry, ensure_ascii=False)
        
        if level == "ERROR":
            self.logger.error(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def log_task_started(self, task_id: str, user_id: str = None, **kwargs):
        """记录任务开始"""
        self.log_event("TASK_STARTED", {
            "task_id": task_id,
            "user_id": user_id,
            **kwargs
        })
    
    def log_task_completed(
        self,
        task_id: str,
        duration: float,
        tokens_used: int,
        success: bool,
        **kwargs
    ):
        """记录任务完成"""
        self.log_event("TASK_COMPLETED", {
            "task_id": task_id,
            "duration": duration,
            "tokens_used": tokens_used,
            "success": success,
            **kwargs
        })
    
    def log_task_failed(
        self,
        task_id: str,
        error_message: str,
        error_type: str = None,
        **kwargs
    ):
        """记录任务失败"""
        self.log_event("TASK_FAILED", {
            "task_id": task_id,
            "error_message": error_message,
            "error_type": error_type,
            **kwargs
        }, level="ERROR")
    
    def log_skill_evolved(
        self,
        skill_id: str,
        old_version: str,
        new_version: str,
        evolution_type: str,
        **kwargs
    ):
        """记录 Skill 进化"""
        self.log_event("SKILL_EVOLVED", {
            "skill_id": skill_id,
            "old_version": old_version,
            "new_version": new_version,
            "evolution_type": evolution_type,  # AUTO-FIX, AUTO-IMPROVE, AUTO-LEARN
            **kwargs
        })
    
    def log_version_created(
        self,
        version_id: str,
        changes_summary: str,
        git_commit: str = None,
        **kwargs
    ):
        """记录版本创建"""
        self.log_event("VERSION_CREATED", {
            "version_id": version_id,
            "changes_summary": changes_summary,
            "git_commit": git_commit,
            **kwargs
        })
    
    def log_ab_test_started(
        self,
        test_id: str,
        version_a: str,
        version_b: str,
        **kwargs
    ):
        """记录 A/B 测试开始"""
        self.log_event("AB_TEST_STARTED", {
            "test_id": test_id,
            "version_a": version_a,
            "version_b": version_b,
            **kwargs
        })
    
    def log_decision_made(
        self,
        decision_type: str,
        score: float,
        recommendation: str,
        reason: str,
        **kwargs
    ):
        """记录决策"""
        self.log_event("DECISION_MADE", {
            "decision_type": decision_type,
            "score": score,
            "recommendation": recommendation,
            "reason": reason,
            **kwargs
        })
    
    def log_rollback_executed(
        self,
        version_id: str,
        rollback_to: str,
        reason: str,
        **kwargs
    ):
        """记录回退执行"""
        self.log_event("ROLLBACK_EXECUTED", {
            "version_id": version_id,
            "rollback_to": rollback_to,
            "reason": reason,
            **kwargs
        }, level="WARNING")
    
    def get_log_file_path(self) -> Path:
        """获取日志文件路径"""
        return self.log_file
    
    def read_recent_events(self, limit: int = 100) -> list:
        """读取最近的事件"""
        if not self.log_file.exists():
            return []
        
        events = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                try:
                    # 提取 JSON 部分
                    json_start = line.find('{')
                    if json_start != -1:
                        event = json.loads(line[json_start:])
                        events.append(event)
                except json.JSONDecodeError:
                    continue
        
        return events
