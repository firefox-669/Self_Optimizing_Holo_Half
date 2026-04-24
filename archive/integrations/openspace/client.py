"""
OpenSpace 客户端
提供 OpenSpace 服务的 Python 接口，实现自我进化
"""

import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime


class OpenSpaceClient:
    """
    OpenSpace 客户端
    用于与 OpenSpace 服务交互，实现技能进化
    """
    
    def __init__(
        self, 
        workspace: str = None,
        skill_dirs: List[str] = None,
        api_key: str = None,
        cloud_enabled: bool = False
    ):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.skill_dirs = skill_dirs or []
        self.api_key = api_key
        self.cloud_enabled = cloud_enabled
        self._connected = False
        self._mcp_process = None
        self._openspace = None
        self._skills: List[Dict] = []
        self._evolution_history: List[Dict] = []
        self._quality_metrics: Dict[str, Any] = {}
    
    async def connect(self) -> bool:
        """连接到 OpenSpace 服务"""
        # 尝试直接导入 OpenSpace
        try:
            from openspace import OpenSpace
            
            self._openspace = OpenSpace(
                workspace=str(self.workspace),
                api_key=self.api_key if self.cloud_enabled else None,
            )
            
            self._connected = True
            self._load_skills()
            return True
        except ImportError:
            # OpenSpace 未安装，记录但不断言失败
            pass
        except Exception as e:
            pass
        
        self._connected = False
        return False
    
    def _load_skills(self):
        """加载已安装的 Skills"""
        if not self._openspace:
            return
        
        try:
            skill_store = getattr(self._openspace, 'skill_store', None)
            if skill_store:
                self._skills = skill_store.list_skills()
        except:
            pass
    
    async def execute(
        self, 
        query: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """执行任务并自动进化"""
        if not self._connected:
            if not await self.connect():
                return {
                    "success": False,
                    "error": "OpenSpace not connected",
                }
        
        try:
            async with self._openspace as os:
                result = await os.execute(query, **kwargs)
                
                evolved = result.get("evolved_skills", [])
                
                if evolved:
                    self._evolution_history.append({
                        "query": query,
                        "evolved_skills": evolved,
                        "timestamp": datetime.now().isoformat(),
                    })
                
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "evolved_skills": evolved,
                    "result": result,
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    async def delegate_task(
        self, 
        task: str,
        mode: str = "auto"
    ) -> Dict[str, Any]:
        """
        通过 delegate-task 工具执行任务
        
        mode: "auto-fix" | "auto-improve" | "auto-learn"
        """
        full_task = f"[{mode}] {task}"
        return await self.execute(full_task)
    
    async def discover_skills(
        self, 
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """搜索 Skills"""
        if not self._connected:
            await self.connect()
        
        if not self._openspace:
            return []
        
        try:
            from openspace import SkillSearch
            
            search = SkillSearch(self._openspace)
            results = await search.search(query, limit=limit)
            return results
        except:
            return []
    
    async def evolve_skill(
        self, 
        skill_name: str,
        mode: str = "auto-fix"
    ) -> Dict[str, Any]:
        """
        进化指定 Skill
        
        mode: "auto-fix" | "auto-improve" | "auto-learn"
        """
        task = f"evolve skill: {skill_name} (mode: {mode})"
        result = await self.execute(task)
        
        self._evolution_history.append({
            "skill_name": skill_name,
            "mode": mode,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })
        
        return result
    
    def get_skills(self) -> List[Dict]:
        """获取已安装的 Skills"""
        return self._skills
    
    def get_evolution_history(self) -> List[Dict]:
        """获取进化历史"""
        return self._evolution_history
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """获取质量指标"""
        return self._quality_metrics
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._connected
    
    async def close(self):
        """关闭连接"""
        if self._openspace:
            try:
                await self._openspace.close()
            except:
                pass
        if self._mcp_process:
            try:
                self._mcp_process.terminate()
            except:
                pass
        self._connected = False
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        return False


class OpenSpaceMCPClient:
    """
    OpenSpace MCP 客户端
    通过 MCP 协议与 OpenSpace 通信
    """
    
    def __init__(
        self, 
        workspace: str = None,
        skill_dirs: List[str] = None,
        api_key: str = None
    ):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.skill_dirs = skill_dirs or []
        self.api_key = api_key
        self._client = None
        self._connected = False
    
    async def connect(self) -> bool:
        """通过 MCP 连接"""
        try:
            from mcp import ClientSession
            
            env = {}
            if self.api_key:
                env["OPENSPACE_API_KEY"] = self.api_key
            if self.skill_dirs:
                env["OPENSPACE_HOST_SKILL_DIRS"] = ",".join(self.skill_dirs)
            env["OPENSPACE_WORKSPACE"] = str(self.workspace)
            
            self._client = ClientSession(
                command="openspace-mcp",
                env=env,
            )
            
            await self._client.initialize()
            self._connected = True
            return True
        except ImportError:
            pass
        except Exception:
            pass
        
        return False
    
    async def call_tool(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any]
    ) -> Any:
        """调用 MCP 工具"""
        if not self._connected:
            await self.connect()
        
        if not self._client:
            return None
        
        return await self._client.call_tool(tool_name, arguments)
    
    async def execute_task(self, task: str) -> Dict[str, Any]:
        """执行任务"""
        result = await self.call_tool(
            "delegate-task",
            {"task": task}
        )
        return result
    
    async def discover_skill(self, query: str) -> List[Dict]:
        """搜索 Skill"""
        result = await self.call_tool(
            "skill-discovery",
            {"query": query}
        )
        return result
    
    async def close(self):
        """关闭连接"""
        if self._client:
            await self._client.close()
        self._connected = False