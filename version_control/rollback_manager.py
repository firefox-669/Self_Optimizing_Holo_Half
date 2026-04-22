"""
回退管理器
管理项目的回退操作
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import shutil

from .snapshot_manager import SnapshotManager


class RollbackManager:
    """
    回退管理器
    支持基于快照和变更历史的回退
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.snapshot_manager = SnapshotManager(str(self.workspace))
        self._rollback_history: List[Dict] = []
        self._load_history()
    
    def _load_history(self):
        """加载回退历史"""
        history_file = self.workspace / ".sohh_cache" / "rollback_history.json"
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                self._rollback_history = json.load(f)
    
    def _save_history(self):
        """保存回退历史"""
        history_file = self.workspace / ".sohh_cache" / "rollback_history.json"
        history_file.parent.mkdir(exist_ok=True)
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(self._rollback_history, f, indent=2, default=str)
    
    async def rollback_to_snapshot(
        self,
        snapshot_id: str,
        reason: str = "",
    ) -> bool:
        """回退到指定快照"""
        # 创建当前状态的备份快照
        await self.snapshot_manager.create_snapshot(
            description=f"Pre-rollbackbackup for {snapshot_id}",
            tags=["rollback_backup"],
        )
        
        # 恢复快照
        success = await self.snapshot_manager.restore_snapshot(snapshot_id)
        
        if success:
            self._rollback_history.append({
                "id": f"rollback_{len(self._rollback_history) + 1}",
                "type": "snapshot",
                "target": snapshot_id,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
            })
            self._save_history()
        
        return success
    
    async def rollback_last_change(
        self,
        reason: str = "",
    ) -> bool:
        """回退上一次变更"""
        if not self._rollback_history:
            return False
        
        last_rollback = self._rollback_history[-1]
        rollback_type = last_rollback.get("type")
        
        if rollback_type == "snapshot":
            return await self.rollback_to_snapshot(
                last_rollback.get("target"),
                reason,
            )
        
        return False
    
    def get_rollback_history(self) -> List[Dict]:
        """获取回退历史"""
        return self._rollback_history
    
    def can_rollback(self) -> bool:
        """检查是否可以回退"""
        return len(self._rollback_history) > 0
    
    def get_last_rollback(self) -> Optional[Dict]:
        """获取上一次回退信息"""
        if self._rollback_history:
            return self._rollback_history[-1]
        return None
    
    async def rollback_capability(
        self,
        capability: str,
        baseline_score: float,
    ):
        """回退能力评分"""
        # 这个需要��合快照和项目自分析
        rollback_entry = {
            "id": f"capability_rollback_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": "capability",
            "capability": capability,
            "baseline_score": baseline_score,
            "timestamp": datetime.now().isoformat(),
        }
        
        self._rollback_history.append(rollback_entry)
        self._save_history()
        
        return rollback_entry