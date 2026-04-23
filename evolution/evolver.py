import os
import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class EvoEngine:
    """
    进化引擎 - 真实集成OpenSpace的自我进化能力
    """

    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.evolution_db = self.workspace / ".sohh_evolution"
        self.evolution_db.mkdir(exist_ok=True)
        
        self._openspace = None
        self._connected = False
        self._evolution_log: List[Dict] = []
        
        self._connect_openspace()

    def _connect_openspace(self):
        """连接真实的OpenSpace"""
        try:
            from openspace import OpenSpace
            
            os.environ.setdefault("OPENSPACE_WORKSPACE", str(self.workspace))
            
            self._openspace = OpenSpace()
            self._connected = True
        except Exception as e:
            print(f"OpenSpace connection failed: {e}")
            self._connected = False

    async def evolve(
        self,
        execution_record: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        通过真实OpenSpace执行进化
        """
        task = execution_record.get("task", "")
        
        if not self._connected or not self._openspace:
            return {
                "evolved": False,
                "skills": [],
                "success": False,
                "error": "OpenSpace not connected",
                "timestamp": datetime.now().isoformat(),
            }

        try:
            result = await self._openspace.execute(f"evolve and improve: {task}")
            
            evolved_skills = result.get("evolved_skills", [])
            
            self._evolution_log.append({
                "task": task,
                "evolved": len(evolved_skills) > 0,
                "skills_count": len(evolved_skills),
                "timestamp": datetime.now().isoformat(),
            })
            
            return {
                "evolved": len(evolved_skills) > 0,
                "skills": evolved_skills,
                "success": True,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "evolved": False,
                "skills": [],
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def evolve_self(self) -> Dict[str, Any]:
        """
        通过OpenSpace进化自身模块
        """
        if not self._connected:
            return {"success": False, "reason": "OpenSpace not connected"}

        self_dir = Path(__file__).parent.parent
        python_files = list(self_dir.glob("**/*.py"))
        python_files = [f for f in python_files if f.name not in ["__init__.py", "evolver.py"]]
        
        results = []
        for py_file in python_files[:5]:
            result = await self.evolve(
                execution_record={"task": f"improve {py_file.name}", "result": {"success": True}},
                context={"module": str(py_file)},
            )
            results.append(result)
        
        successful = sum(1 for r in results if r.get("success"))
        
        return {
            "success": True,
            "total": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "details": results,
        }

    async def evolve_project_skills(
        self,
        project_path: str,
    ) -> Dict[str, Any]:
        """
        通过OpenSpace帮助其他项目进化skills
        """
        if not self._connected:
            return {"success": False, "reason": "OpenSpace not connected"}

        project = Path(project_path)
        if not project.exists():
            return {"success": False, "reason": "project not found"}

        project_name = project.name
        
        try:
            result = await self._openspace.execute(
                f"evolve all skills in {project_path}"
            )
            
            evolved_skills = result.get("evolved_skills", [])
            
            return {
                "success": True,
                "project": project_name,
                "skills_evolved": len(evolved_skills),
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_evolution_log(self) -> List[Dict]:
        return self._evolution_log

    def is_connected(self) -> bool:
        return self._connected

    async def shutdown(self):
        if self._openspace:
            await self._openspace.close()
