import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class SafetyMonitor:
    """
    群体安全监控
    实时监控多个 Agent 的执行安全状态
    """

    def __init__(self):
        self._active_executions: Dict[str, Dict] = {}
        self._execution_logs: List[Dict] = []
        self._safety_rules = self._load_safety_rules()
        
        self._max_concurrent_agents = 10
        self._alert_threshold = 0.8
        
        self._monitoring_task: Optional[asyncio.Task] = None

    def _load_safety_rules(self) -> Dict[str, Any]:
        """加载安全规则"""
        return {
            "max_file_modifications": 50,
            "max_execution_time": 600,
            "dangerous_patterns": [
                "rm -rf /",
                "format c:",
                "del /f /s /q",
                "DROP DATABASE",
                "DELETE FROM.*WHERE",
                "eval\\(",
                "exec\\(",
                "__import__",
            ],
            "allowed_extensions": [
                ".py", ".js", ".ts", ".jsx", ".tsx", ".md", ".json",
                ".yaml", ".yml", ".toml", ".cfg", ".ini", ".txt",
                ".html", ".css", ".sh", ".bat", ".ps1",
            ],
        }

    async def start_monitoring(self, execution_id: str):
        """开始监控"""
        self._active_executions[execution_id] = {
            "id": execution_id,
            "start_time": datetime.now(),
            "status": "running",
            "safety_score": 1.0,
            "modifications": [],
        }
        
        if self._monitoring_task is None:
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def _monitoring_loop(self):
        """监控循环"""
        while self._active_executions:
            await asyncio.sleep(1)
            await self._check_safety()

    async def _check_safety(self):
        """检查安全状态"""
        now = datetime.now()
        
        for exec_id, execution in list(self._active_executions.items()):
            start_time = execution.get("start_time")
            if start_time:
                elapsed = (now - start_time).total_seconds()
                
                if elapsed > self._safety_rules["max_execution_time"]:
                    execution["status"] = "timeout"
                    execution["safety_score"] = 0.5
                    
                    await self._flag_safety_issue(exec_id, "execution_timeout")
            
            modifications = execution.get("modifications", [])
            if len(modifications) > self._safety_rules["max_file_modifications"]:
                await self._flag_safety_issue(exec_id, "too_many_modifications")

    async def _flag_safety_issue(self, execution_id: str, issue_type: str):
        """标记安全问题"""
        if execution_id in self._active_executions:
            execution = self._active_executions[execution_id]
            execution["safety_score"] *= 0.8
            
            log_entry = {
                "execution_id": execution_id,
                "issue_type": issue_type,
                "timestamp": datetime.now().isoformat(),
                "safety_score": execution.get("safety_score", 0.0),
            }
            self._execution_logs.append(log_entry)

    async def check_execution_safety(
        self,
        execution_id: str,
        result: Dict[str, Any],
    ):
        """检查执行结果的安全性"""
        if execution_id not in self._active_executions:
            return
        
        execution = self._active_executions[execution_id]
        
        actions = result.get("actions", [])
        for action in actions:
            action_type = action.get("type", "")
            
            if action_type in ["file_create", "file_edit", "file_delete"]:
                execution["modifications"].append(action)
            
            if action_type == "run_command":
                command = action.get("command", "")
                if self._is_dangerous_command(command):
                    await self._flag_safety_issue(execution_id, "dangerous_command")
        
        final_score = execution.get("safety_score", 1.0)
        if final_score >= self._alert_threshold:
            execution["status"] = "safe"
        else:
            execution["status"] = "unsafe"
        
        result["safety"] = {
            "score": final_score,
            "status": execution["status"],
            "issues": self._get_issues_for_execution(execution_id),
        }

    def _is_dangerous_command(self, command: str) -> bool:
        """检查危险命令"""
        command_lower = command.lower()
        for pattern in self._safety_rules["dangerous_patterns"]:
            if pattern.lower() in command_lower:
                return True
        return False

    def _get_issues_for_execution(self, execution_id: str) -> List[Dict]:
        """获取执行的问题"""
        return [
            log for log in self._execution_logs
            if log.get("execution_id") == execution_id
        ]

    async def stop_monitoring(self, execution_id: str):
        """停止监控"""
        if execution_id in self._active_executions:
            execution = self._active_executions[execution_id]
            execution["end_time"] = datetime.now()
            execution["status"] = "completed"
            
            self._execution_logs.append({
                "execution_id": execution_id,
                "event": "completed",
                "timestamp": datetime.now().isoformat(),
            })
            
            del self._active_executions[execution_id]

    def get_active_executions(self) -> List[Dict]:
        """获取活跃执行"""
        return list(self._active_executions.values())

    def get_safety_logs(self) -> List[Dict]:
        """获取安全日志"""
        return self._execution_logs

    async def shutdown(self):
        """关闭监控"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        self._active_executions.clear()