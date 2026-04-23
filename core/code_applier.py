"""
代码应用器
安全地应用代码修改，支持自动回退
"""

import os
import ast
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CodeApplier:
    """
    代码应用器
    
    安全地应用代码修改，如果出现问题可以自动回退
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.backup_dir = self.workspace / ".sohh_cache" / "code_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    async def apply_code_patch(
        self, 
        patch: Dict[str, Any],
        run_tests: bool = True
    ) -> Dict[str, Any]:
        """
        应用代码补丁
        
        Args:
            patch: 代码补丁字典，包含：
                - files_to_modify: 要修改的文件列表
                - new_files: 新文件列表
                - deleted_files: 要删除的文件列表
            run_tests: 是否运行测试验证
            
        Returns:
            {
                "success": bool,
                "modified_files": [...],
                "new_files": [...],
                "error": str or None,
                "backup_id": str
            }
        """
        result = {
            "success": False,
            "modified_files": [],
            "new_files": [],
            "deleted_files": [],
            "error": None,
            "backup_id": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # 1. 创建备份
            backup_id = await self._create_backup()
            result["backup_id"] = backup_id
            
            # 2. 应用新文件
            for new_file in patch.get("new_files", []):
                await self._create_new_file(new_file)
                result["new_files"].append(new_file["file_path"])
            
            # 3. 修改现有文件
            for file_mod in patch.get("files_to_modify", []):
                await self._modify_file(file_mod)
                result["modified_files"].append(file_mod["file_path"])
            
            # 4. 删除文件
            for del_file in patch.get("deleted_files", []):
                await self._delete_file(del_file)
                result["deleted_files"].append(del_file)
            
            # 5. 语法检查
            syntax_ok = await self._check_syntax(result["modified_files"] + result["new_files"])
            if not syntax_ok:
                raise ValueError("Syntax check failed")
            
            # 6. 运行测试（可选）
            if run_tests:
                tests_passed = await self._run_tests()
                if not tests_passed:
                    raise ValueError("Tests failed")
            
            # 7. 成功，清理旧备份
            result["success"] = True
            logger.info(f"✅ Code patch applied successfully (backup: {backup_id})")
            
            return result
        
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"❌ Failed to apply code patch: {e}")
            
            # 自动回退
            if result["backup_id"]:
                await self.rollback(result["backup_id"])
                logger.info(f"🔄 Automatically rolled back to backup {result['backup_id']}")
            
            return result
    
    async def _create_backup(self) -> str:
        """创建代码备份"""
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_id
        
        # 备份所有 Python 文件
        python_files = list(self.workspace.rglob("*.py"))
        
        for py_file in python_files:
            # 跳过缓存目录
            if ".sohh_cache" in str(py_file) or "__pycache__" in str(py_file):
                continue
            
            rel_path = py_file.relative_to(self.workspace)
            backup_file = backup_path / rel_path
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(py_file, backup_file)
        
        logger.info(f"💾 Created backup: {backup_id} ({len(python_files)} files)")
        return backup_id
    
    async def _create_new_file(self, new_file: Dict[str, str]):
        """创建新文件"""
        file_path = self.workspace / new_file["file_path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(new_file["content"], encoding="utf-8")
        logger.info(f"📄 Created new file: {new_file['file_path']}")
    
    async def _modify_file(self, file_mod: Dict[str, Any]):
        """修改现有文件"""
        file_path = self.workspace / file_mod["file_path"]
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 读取原文件
        lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
        
        # 应用修改
        for change in file_mod.get("changes", []):
            line_start = change.get("line_start", 1) - 1  # 转为 0-based
            line_end = change.get("line_end", len(lines))
            new_code = change.get("new_code", "")
            
            # 替换指定行
            lines[line_start:line_end] = [new_code + "\n"]
        
        # 写回文件
        file_path.write_text("".join(lines), encoding="utf-8")
        logger.info(f"✏️  Modified file: {file_mod['file_path']}")
    
    async def _delete_file(self, file_path_str: str):
        """删除文件"""
        file_path = self.workspace / file_path_str
        if file_path.exists():
            file_path.unlink()
            logger.info(f"🗑️  Deleted file: {file_path_str}")
    
    async def _check_syntax(self, files: List[str]) -> bool:
        """检查 Python 语法"""
        for file_path_str in files:
            file_path = self.workspace / file_path_str
            
            if not file_path.exists() or not file_path.suffix == '.py':
                continue
            
            try:
                code = file_path.read_text(encoding="utf-8")
                ast.parse(code)
            except SyntaxError as e:
                logger.error(f"❌ Syntax error in {file_path_str}: {e}")
                return False
        
        return True
    
    async def _run_tests(self) -> bool:
        """运行测试"""
        import subprocess
        
        # 查找测试文件
        test_dir = self.workspace / "tests"
        if not test_dir.exists():
            logger.warning("⚠️  No tests directory found, skipping tests")
            return True
        
        try:
            # 运行 pytest
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                cwd=str(self.workspace),
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                logger.info("✅ All tests passed")
                return True
            else:
                logger.error(f"❌ Tests failed:\n{result.stdout}\n{result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            logger.error("❌ Tests timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to run tests: {e}")
            return False
    
    async def rollback(self, backup_id: str) -> bool:
        """
        回退到指定备份
        
        Args:
            backup_id: 备份 ID
            
        Returns:
            是否成功回退
        """
        backup_path = self.backup_dir / backup_id
        
        if not backup_path.exists():
            logger.error(f"❌ Backup not found: {backup_id}")
            return False
        
        try:
            # 恢复所有文件
            for backup_file in backup_path.rglob("*"):
                if backup_file.is_file():
                    rel_path = backup_file.relative_to(backup_path)
                    target_file = self.workspace / rel_path
                    
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup_file, target_file)
            
            logger.info(f"✅ Rolled back to backup: {backup_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to rollback: {e}")
            return False
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份"""
        backups = []
        
        for backup_dir in sorted(self.backup_dir.iterdir()):
            if backup_dir.is_dir():
                backups.append({
                    "backup_id": backup_dir.name,
                    "created_at": backup_dir.stat().st_mtime,
                    "file_count": len(list(backup_dir.rglob("*.py")))
                })
        
        return backups
    
    async def cleanup_old_backups(self, keep_last: int = 10):
        """清理旧备份，只保留最近的 N 个"""
        backups = await self.list_backups()
        
        if len(backups) > keep_last:
            # 按时间排序，删除旧的
            backups.sort(key=lambda x: x["created_at"])
            
            for backup in backups[:-keep_last]:
                backup_path = self.backup_dir / backup["backup_id"]
                shutil.rmtree(backup_path)
                logger.info(f"🗑️  Cleaned up old backup: {backup['backup_id']}")
