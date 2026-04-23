"""
安全进化控制器
提供安全的自我进化机制，风险最小化
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from optimizer import AutoOptimizer
from version_control import SnapshotManager, ChangeLogger


class SafetyLevel(Enum):
    """安全级别"""
    DISABLED = 0      # 完全禁用自动进化
    READ_ONLY = 1     # 仅分析，不修改
    DRY_RUN = 2       # 测试运行，不保存
    SAFE_ONLY = 3       # 仅安全的修改
    FULL = 4          # 完全自动


class SafetyEvolutionController:
    """
    安全进化控制器
    最小化自我进化的风险
    """
    
    def __init__(
        self,
        workspace: str = None,
        safety_level: SafetyLevel = SafetyLevel.SAFE_ONLY,
        min_priority_threshold: float = 0.7,
    ):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        
        # 安全级别
        self.safety_level = safety_level
        self.min_priority = min_priority_threshold
        
        # 必需组件
        self.optimizer = AutoOptimizer(str(self.workspace))
        self.snapshot_manager = SnapshotManager(str(self.workspace))
        self.change_logger = ChangeLogger(str(self.workspace))
        
        # 统计
        self._applied_count = 0
        self._rolled_back_count = 0
        self._failed_count = 0
    
    def set_safety_level(self, level: SafetyLevel):
        """设置安全级别"""
        self.safety_level = level
    
    def get_safety_level(self) -> SafetyLevel:
        """获取安全级别"""
        return self.safety_level
    
    async def safe_evolve(
        self,
        suggestions: List[Dict],
        dry_run: bool = None,
    ) -> Dict[str, Any]:
        """
        安全进化
        
        Args:
            suggestions: Evolution Suggestions 列表
            dry_run: 是否仅测试不应用 (覆盖安全级别)
        
        Returns:
            包含结果和统计的安全报告
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "safety_level": self.safety_level.value,
            "suggestions_reviewed": len(suggestions),
            "suggestions_applied": 0,
            "suggestions_rolled_back": 0,
            "suggestions_failed": 0,
            "applied_details": [],
            "failed_details": [],
        }
        
        # 检查安全级别
        actual_dry_run = dry_run if dry_run is not None else (self.safety_level.value < SafetyLevel.SAFE_ONLY.value)
        
        if self.safety_level == SafetyLevel.DISABLED:
            result["status"] = "disabled"
            result["message"] = "自动进化已禁用"
            return result
        
        if self.safety_level == SafetyLevel.READ_ONLY:
            result["status"] = "read_only"
            result["message"] = "仅分析模式，不进行修改"
            result["safe_suggestions"] = self._filter_safe(suggestions)
            return result
        
        # 设置最低优先级
        safe_suggestions = [
            s for s in suggestions 
            if s.get("priority", 0) >= self.min_priority
        ]
        safe_suggestions = self._filter_safe(safe_suggestions)
        
        for suggestion in safe_suggestions:
            apply_result = await self._apply_single_safe(
                suggestion,
                dry_run=actual_dry_run,
            )
            
            if apply_result["success"]:
                result["suggestions_applied"] += 1
                result["applied_details"].append(apply_result)
            else:
                result["suggestions_failed"] += 1
                result["failed_details"].append(apply_result)
        
        result["status"] = "completed"
        
        # 更新统计
        self._applied_count = result["suggestions_applied"]
        self._failed_count = result["suggestions_failed"]
        
        return result
    
    def _filter_safe(self, suggestions: List[Dict]) -> List[Dict]:
        """过滤安全的建议"""
        safe = []
        
        unsafe_types = {
            "connection": False,  # 连接外部服务 - 安全
            "capability_enhancement": True,  # 能力增强 - 需要确认
            "feature_enhancement": True,
            "new_feature": True,
            "version_update": False,  # 版本更新 - 安全
            "skill_capture": False,  # Skill 捕获 - 安全
        }
        
        for s in suggestions:
            s_type = s.get("type", "")
            target = s.get("target", "")
            
            # 危险操作过滤
            if target == "both":
                continue  # 跳过跨组件修改
            
            # 检查类型是否安全
            is_safe = unsafe_types.get(s_type, True)
            if is_safe is False:
                safe.append(s)
            elif self.safety_level == SafetyLevel.FULL:
                safe.append(s)
        
        return safe
    
    async def _apply_single_safe(
        self,
        suggestion: Dict,
        dry_run: bool,
    ) -> Dict[str, Any]:
        """安全应用单个建议"""
        
        if dry_run:
            return {
                "success": True,
                "suggestion_id": suggestion.get("id"),
                "dry_run": True,
                "would_apply": True,
            }
        
        # 创建备份快照
        snapshot_id = await self.snapshot_manager.create_snapshot(
            description=f"Pre-evolution: {suggestion.get('title')}",
            tags=["safety_backup"],
        )
        
        try:
            # 应用优化
            apply_result = await self.optimizer.apply_optimization(suggestion)
            
            if apply_result.get("applied"):
                # 验证应用结果
                verification = await self._verify_application(suggestion)
                
                if verification["success"]:
                    self.change_logger.log_optimization(
                        suggestion,
                        "applied",
                        None,
                        None,
                    )
                    return {
                        "success": True,
                        "suggestion_id": suggestion.get("id"),
                        "snapshot_id": snapshot_id,
                        "verified": True,
                    }
                else:
                    # 验证失败，回退
                    await self.snapshot_manager.restore_snapshot(snapshot_id)
                    self._rolled_back_count += 1
                    return {
                        "success": False,
                        "suggestion_id": suggestion.get("id"),
                        "reason": "verification_failed",
                        "rolled_back": True,
                    }
            else:
                return {
                    "success": False,
                    "suggestion_id": suggestion.get("id"),
                    "error": apply_result.get("error"),
                }
        
        except Exception as e:
            # 异常回退
            await self.snapshot_manager.restore_snapshot(snapshot_id)
            self._rolled_back_count += 1
            return {
                "success": False,
                "suggestion_id": suggestion.get("id"),
                "error": str(e),
                "rolled_back": True,
            }
    
    async def _verify_application(
        self,
        suggestion: Dict,
    ) -> Dict[str, Any]:
        """验证应用结果"""
        
        # 基本验证：检查项目仍可导入
        try:
            import importlib
            import sys
            
            # 重新加载模块
            module_name = "Self_Optimizing_Holo_Half"
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            
            return {"success": True}
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取安全统计"""
        return {
            "safety_level": self.safety_level.value,
            "safety_level_name": self.safety_level.name,
            "min_priority": self.min_priority,
            "applied_count": self._applied_count,
            "rolled_back_count": self._rolled_back_count,
            "failed_count": self._failed_count,
            "success_rate": (
                self._applied_count / max(1, self._applied_count + self._failed_count)
            ) if self._applied_count + self._failed_count > 0 else 0,
        }


class ApprovalQueue:
    """
    审批队列
    需要手动确认的建议
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self._queue: List[Dict] = []
        self._load_queue()
    
    def _load_queue(self):
        """加载队列"""
        queue_file = self.workspace / ".sohh_cache" / "approval_queue.json"
        if queue_file.exists():
            import json
            with open(queue_file) as f:
                self._queue = json.load(f)
    
    def _save_queue(self):
        """保存队列"""
        queue_file = self.workspace / ".sohh_cache" / "approval_queue.json"
        queue_file.parent.mkdir(exist_ok=True)
        import json
        with open(queue_file, "w") as f:
            json.dump(self._queue, f, indent=2)
    
    def add(self, suggestion: Dict):
        """添加到审批队列"""
        suggestion["status"] = "pending"
        suggestion["added_at"] = datetime.now().isoformat()
        self._queue.append(suggestion)
        self._save_queue()
    
    def approve(self, suggestion_id: str) -> bool:
        """批准建议"""
        for s in self._queue:
            if s.get("id") == suggestion_id:
                s["status"] = "approved"
                s["approved_at"] = datetime.now().isoformat()
                self._save_queue()
                return True
        return False
    
    def reject(self, suggestion_id: str) -> bool:
        """拒绝建议"""
        for s in self._queue:
            if s.get("id") == suggestion_id:
                s["status"] = "rejected"
                s["rejected_at"] = datetime.now().isoformat()
                self._save_queue()
                return True
        return False
    
    def get_pending(self) -> List[Dict]:
        """获取待审批的建议"""
        return [s for s in self._queue if s.get("status") == "pending"]
    
    def get_all(self) -> List[Dict]:
        """获取所有建议"""
        return self._queue