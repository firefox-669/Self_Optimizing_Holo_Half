"""
变更记录器
记录项目所有的变更历史
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime


class ChangeLogger:
    """
    变更记录器
    记录项目变更历史
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.changes_dir = self.workspace / ".sohh_cache" / "changes"
        self.changes_dir.mkdir(exist_ok=True)
        self._changes: List[Dict] = []
        self._load_changes()
    
    def _load_changes(self):
        """加载变更记录"""
        changes_file = self.changes_dir / "all_changes.json"
        if changes_file.exists():
            with open(changes_file, "r", encoding="utf-8") as f:
                self._changes = json.load(f)
    
    def _save_changes(self):
        """保存变更记录"""
        changes_file = self.changes_dir / "all_changes.json"
        with open(changes_file, "w", encoding="utf-8") as f:
            json.dump(self._changes, f, indent=2, default=str)
    
    def log_change(
        self,
        change_type: str,
        description: str,
        details: Dict[str, Any] = None,
        suggestion_id: str = None,
    ):
        """记录变更"""
        change = {
            "id": f"change_{len(self._changes) + 1}",
            "type": change_type,
            "description": description,
            "details": details or {},
            "suggestion_id": suggestion_id,
            "timestamp": datetime.now().isoformat(),
            "status": "applied",
        }
        
        self._changes.append(change)
        self._save_changes()
        
        return change["id"]
    
    def log_optimization(
        self,
        suggestion: Dict[str, Any],
        result: str,
        before_score: float = None,
        after_score: float = None,
    ):
        """记录优化"""
        details = {
            "suggestion_id": suggestion.get("id"),
            "target": suggestion.get("target"),
            "type": suggestion.get("type"),
            "title": suggestion.get("title"),
            "result": result,
        }
        
        if before_score is not None:
            details["before_score"] = before_score
        if after_score is not None:
            details["after_score"] = after_score
        
        if before_score is not None and after_score is not None:
            details["delta"] = after_score - before_score
        
        return self.log_change(
            change_type="optimization",
            description=f"优化: {suggestion.get('title', '')}",
            details=details,
            suggestion_id=suggestion.get("id"),
        )
    
    def log_capability_change(
        self,
        capability: str,
        before: float,
        after: float,
    ):
        """记录能力变化"""
        details = {
            "capability": capability,
            "before": before,
            "after": after,
            "delta": after - before,
        }
        
        return self.log_change(
            change_type="capability_change",
            description=f"能力变化: {capability} ({before} -> {after})",
            details=details,
        )
    
    def log_module_change(
        self,
        module: str,
        action: str,
        file_count: int = 0,
    ):
        """记录模块变化"""
        details = {
            "module": module,
            "action": action,
            "file_count": file_count,
        }
        
        return self.log_change(
            change_type="module_change",
            description=f"模块变化: {module} ({action})",
            details=details,
        )
    
    def get_changes(
        self, 
        change_type: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """获取变更记录"""
        changes = self._changes
        
        if change_type:
            changes = [c for c in changes if c.get("type") == change_type]
        
        return changes[:limit]
    
    def get_recent_changes(self, days: int = 7) -> List[Dict]:
        """获取最近的变更"""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        
        for change in self._changes:
            timestamp = change.get("timestamp", "")
            if not timestamp:
                continue
            
            try:
                dt = datetime.fromisoformat(timestamp)
                if dt >= cutoff:
                    recent.append(change)
            except:
                pass
        
        return recent
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取变更统计"""
        stats = {
            "total_changes": len(self._changes),
            "by_type": {},
            "recent_count": len(self.get_recent_changes()),
        }
        
        for change in self._changes:
            change_type = change.get("type", "unknown")
            stats["by_type"][change_type] = stats["by_type"].get(change_type, 0) + 1
        
        return stats
    
    def clear_old_changes(self, days: int = 30):
        """清理旧变更记录"""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        
        remaining = []
        for change in self._changes:
            timestamp = change.get("timestamp", "")
            if not timestamp:
                continue
            
            try:
                dt = datetime.fromisoformat(timestamp)
                if dt >= cutoff:
                    remaining.append(change)
            except:
                pass
        
        self._changes = remaining
        self._save_changes()