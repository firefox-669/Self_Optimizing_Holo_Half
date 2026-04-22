"""
快照管理器
负责创建和管理项目快照
"""

import asyncio
import shutil
import tarfile
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import hashlib


class SnapshotManager:
    """
    快照管理器
    创建、存储、恢复到项目快照
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.snapshot_dir = self.workspace / ".sohh_snapshots"
        self.snapshot_dir.mkdir(exist_ok=True)
        self._snapshots: Dict[str, Dict] = {}
        self._load_index()
    
    def _load_index(self):
        """加载快照索引"""
        index_file = self.snapshot_dir / "index.json"
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                self._snapshots = json.load(f)
    
    def _save_index(self):
        """保存快照索引"""
        index_file = self.snapshot_dir / "index.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(self._snapshots, f, indent=2, default=str)
    
    async def create_snapshot(
        self, 
        description: str = "",
        tags: List[str] = None
    ) -> str:
        """创建项目快照"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_id = f"snap_{timestamp}"
        
        snapshot_info = {
            "id": snapshot_id,
            "description": description,
            "tags": tags or [],
            "timestamp": datetime.now().isoformat(),
            "workspace": str(self.workspace),
            "files": [],
            "size": 0,
        }
        
        # 收集项目文件
        project_files = []
        ignore_patterns = {
            "__pycache__", ".git", ".sohh_cache", 
            ".sohh_snapshots", "*.pyc", "node_modules",
            ".venv", "venv", ".env"
        }
        
        for file_path in self.workspace.rglob("*"):
            if not file_path.is_file():
                continue
            
            # 检查是否应该忽略
            should_ignore = False
            for pattern in ignore_patterns:
                if pattern in str(file_path):
                    should_ignore = True
                    break
            
            if should_ignore:
                continue
            
            relative_path = file_path.relative_to(self.workspace)
            project_files.append({
                "path": str(relative_path),
                "size": file_path.stat().st_size,
            })
        
        snapshot_info["files"] = project_files
        snapshot_info["file_count"] = len(project_files)
        
        # 创建压缩包
        snapshot_file = self.snapshot_dir / f"{snapshot_id}.tar.gz"
        
        with tarfile.open(snapshot_file, "w:gz") as tar:
            # 添加元数据
            meta_file = self.snapshot_dir / f"{snapshot_id}_meta.json"
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(snapshot_info, f, indent=2, default=str)
            
            tar.add(meta_file, arcname="metadata.json")
            meta_file.unlink()
            
            # 添加项目文��
            for file_info in project_files:
                file_path = self.workspace / file_info["path"]
                try:
                    tar.add(file_path, arcname=file_info["path"])
                except:
                    pass
        
        # 计算大小
        if snapshot_file.exists():
            snapshot_info["size"] = snapshot_file.stat().st_size
        
        # 保存索引
        self._snapshots[snapshot_id] = snapshot_info
        self._save_index()
        
        return snapshot_id
    
    async def restore_snapshot(
        self, 
        snapshot_id: str,
        target_dir: str = None
    ) -> bool:
        """恢复快照"""
        if snapshot_id not in self._snapshots:
            return False
        
        target = Path(target_dir) if target_dir else self.workspace
        snapshot_file = self.snapshot_dir / f"{snapshot_id}.tar.gz"
        
        if not snapshot_file.exists():
            return False
        
        try:
            # 解压到目标目录
            with tarfile.open(snapshot_file, "r:gz") as tar:
                tar.extractall(target)
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
    
    def list_snapshots(self) -> List[Dict]:
        """列出所有快照"""
        result = []
        for snap_id, info in self._snapshots.items():
            result.append({
                "id": snap_id,
                "description": info.get("description", ""),
                "timestamp": info.get("timestamp", ""),
                "file_count": info.get("file_count", 0),
                "size": info.get("size", 0),
                "tags": info.get("tags", []),
            })
        
        return sorted(result, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def get_snapshot_info(self, snapshot_id: str) -> Optional[Dict]:
        """获取快照信息"""
        return self._snapshots.get(snapshot_id)
    
    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """删除快照"""
        if snapshot_id not in self._snapshots:
            return False
        
        snapshot_file = self.snapshot_dir / f"{snapshot_id}.tar.gz"
        if snapshot_file.exists():
            snapshot_file.unlink()
        
        del self._snapshots[snapshot_id]
        self._save_index()
        
        return True
    
    async def diff(
        self, 
        snapshot_a: str, 
        snapshot_b: str
    ) -> Dict[str, Any]:
        """对比两个快照"""
        info_a = self._snapshots.get(snapshot_a)
        info_b = self._snapshots.get(snapshot_b)
        
        if not info_a or not info_b:
            return {"error": "Snapshot not found"}
        
        files_a = {f["path"] for f in info_a.get("files", [])}
        files_b = {f["path"] for f in info_b.get("files", [])}
        
        added = files_b - files_a
        removed = files_a - files_b
        common = files_a & files_b
        
        return {
            "snapshot_a": snapshot_a,
            "snapshot_b": snapshot_b,
            "added": list(added),
            "removed": list(removed),
            "common": len(common),
        }
    
    def cleanup_old_snapshots(self, keep_count: int = 10):
        """清理旧快照"""
        snapshots = self.list_snapshots()
        
        if len(snapshots) <= keep_count:
            return
        
        to_delete = snapshots[keep_count:]
        
        for snap in to_delete:
            asyncio.create_task(self.delete_snapshot(snap["id"]))