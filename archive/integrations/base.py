"""
MCP 集成基类
提供 OpenHands 和 OpenSpace 的统一接口
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path


class MCPIntegration(ABC):
    """
    MCP 集成基类
    定义外部集成的统一接口
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self._connected = False
        self._last_connectAttempt = None
        self._connection_timeout = 30
        self._error_history: List[Dict] = []
    
    @abstractmethod
    async def connect(self) -> bool:
        """连接到外部服务"""
        pass
    
    @abstractmethod
    async def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """执行任务"""
        pass
    
    @abstractmethod
    async def get_tools(self) -> List[Dict]:
        """获取可用工具列表"""
        pass
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._connected
    
    async def reconnect(self) -> bool:
        """重新连接"""
        self._connected = False
        return await self.connect()
    
    def _log_error(self, error: str, details: Dict = None):
        """记录错误"""
        self._error_history.append({
            "error": error,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        })
        if len(self._error_history) > 100:
            self._error_history = self._error_history[-100:]
    
    def get_error_history(self) -> List[Dict]:
        """获取错误历史"""
        return self._error_history
    
    async def close(self):
        """关闭连接"""
        self._connected = False
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        return False


class OpenHandsIntegration(MCPIntegration):
    """
    OpenHands 集成
    通过 MCP 与 OpenHands 服务通信
    """
    
    def __init__(
        self, 
        workspace: str = None,
        base_url: str = "http://localhost:3000",
        config_path: str = None
    ):
        super().__init__(workspace)
        self.base_url = base_url
        self.config_path = config_path
        self._runtime = None
        self._available_tools: List[Dict] = []
    
    async def connect(self) -> bool:
        """连接到 OpenHands 服务"""
        try:
            import aiohttp
            session = aiohttp.ClientSession()
            
            async with session.get(
                f"{self.base_url}/api/status",
                timeout=aiohttp.ClientTimeout(total=self._connection_timeout)
            ) as resp:
                if resp.status == 200:
                    self._connected = True
                    await session.close()
                    return True
            
            await session.close()
        except Exception as e:
            self._log_error("OpenHands connection failed", {"error": str(e)})
        
        # 如果无法连接，尝试使用 SDK 模式
        return await self._connect_via_sdk()
    
    async def _connect_via_sdk(self) -> bool:
        """通过 SDK 连接"""
        try:
            from openhands import runtime as oh_runtime
            
            if self.config_path:
                config_file = Path(self.config_path)
                if config_file.exists():
                    import toml
                    with open(config_file) as f:
                        config = toml.load(f)
                    self._runtime = oh_runtime.OpenHandsRuntime(config=config)
                else:
                    self._runtime = oh_runtime.OpenHandsRuntime(
                        workspace=str(self.workspace)
                    )
            else:
                self._runtime = oh_runtime.OpenHandsRuntime(
                    workspace=str(self.workspace)
                )
            
            self._connected = True
            return True
        except ImportError:
            self._log_error("OpenHands SDK not installed")
        except Exception as e:
            self._log_error("OpenHands SDK connection failed", {"error": str(e)})
        
        self._connected = False
        return False
    
    async def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """执行任务"""
        if not self._connected:
            if not await self.connect():
                return {
                    "success": False,
                    "error": "OpenHands not connected",
                    "fallback": False,
                }
        
        # 使用 SDK 执行
        if self._runtime:
            try:
                result = await self._runtime.run(
                    instruction=task,
                    workspace=str(self.workspace),
                    **kwargs
                )
                return {
                    "success": True,
                    "result": result,
                    "output": result.get("output", ""),
                }
            except Exception as e:
                self._log_error("Execution failed", {"error": str(e)})
                return {
                    "success": False,
                    "error": str(e),
                }
        
        # Fallback: 返回错误
        return {
            "success": False,
            "error": "No runtime available",
            "fallback": True,
        }
    
    async def get_tools(self) -> List[Dict]:
        """获取可用工具"""
        if not self._connected:
            await self.connect()
        
        return self._available_tools
    
    async def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "connected": self._connected,
            "runtime": "sdk" if self._runtime else "http",
            "workspace": str(self.workspace),
            "last_error": self._error_history[-1] if self._error_history else None,
        }
    
    async def close(self):
        """关闭连接"""
        if self._runtime:
            try:
                await self._runtime.close()
            except:
                pass
        self._connected = False


class OpenSpaceIntegration(MCPIntegration):
    """
    OpenSpace 集成
    通过 MCP 与 OpenSpace 服务通信，实现自我进化
    """
    
    def __init__(
        self, 
        workspace: str = None,
        skill_dirs: List[str] = None,
        api_key: str = None
    ):
        super().__init__(workspace)
        self.skill_dirs = skill_dirs or []
        self.api_key = api_key
        self._mcp_process = None
        self._skills: List[Dict] = []
        self._evolution_history: List[Dict] = []
        self._quality_metrics: Dict[str, Any] = {}
    
    async def connect(self) -> bool:
        """连接到 OpenSpace 服务"""
        # 尝试通过 MCP 连接
        return await self._connect_mcp()
    
    async def _connect_mcp(self) -> bool:
        """通过 MCP 连接 OpenSpace"""
        try:
            import subprocess
            import os
            
            env = os.environ.copy()
            if self.api_key:
                env["OPENSPACE_API_KEY"] = self.api_key
            if self.skill_dirs:
                env["OPENSPACE_HOST_SKILL_DIRS"] = ",".join(self.skill_dirs)
            env["OPENSPACE_WORKSPACE"] = str(self.workspace)
            
            self._mcp_process = subprocess.Popen(
                ["openspace-mcp"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            self._connected = True
            return True
        except FileNotFoundError:
            self._log_error("openspace-mcp not found")
        except Exception as e:
            self._log_error("OpenSpace MCP connection failed", {"error": str(e)})
        
        # 尝试直接导入
        return await self._connect_direct()
    
    async def _connect_direct(self) -> bool:
        """直接导入 OpenSpace"""
        try:
            from openspace import OpenSpace
            
            self._openspace = OpenSpace(
                workspace=str(self.workspace),
                api_key=self.api_key,
            )
            
            self._connected = True
            return True
        except ImportError:
            self._log_error("OpenSpace not installed")
        except Exception as e:
            self._log_error("OpenSpace connection failed", {"error": str(e)})
        
        self._connected = False
        return False
    
    async def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """执行任务"""
        if not self._connected:
            if not await self.connect():
                return {
                    "success": False,
                    "error": "OpenSpace not connected",
                }
        
        try:
            from openspace import OpenSpace
            
            async with OpenSpace(
                workspace=str(self.workspace),
                api_key=self.api_key,
            ) as os:
                result = await os.execute(task, **kwargs)
                
                self._evolution_history.append({
                    "task": task,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                })
                
                return {
                    "success": True,
                    "result": result,
                    "evolved_skills": result.get("evolved_skills", []),
                }
        except Exception as e:
            self._log_error("Execution failed", {"error": str(e)})
            return {
                "success": False,
                "error": str(e),
            }
    
    async def get_tools(self) -> List[Dict]:
        """获取 MCP 工具"""
        return [
            {
                "name": "delegate-task",
                "description": "Execute task via OpenSpace",
            },
            {
                "name": "skill-discovery", 
                "description": "Search and discover skills",
            },
            {
                "name": "evolve-skill",
                "description": "Evolve a skill",
            },
        ]
    
    async def get_skills(self) -> List[Dict]:
        """获取已安装的 Skills"""
        return self._skills
    
    async def evolve_skill(
        self, 
        skill_name: str, 
        mode: str = "auto"
    ) -> Dict[str, Any]:
        """
        进化 Skill
        
        mode: "auto-fix" | "auto-improve" | "auto-learn"
        """
        if not self._connected:
            await self.connect()
        
        task = f"evolve skill: {skill_name} (mode: {mode})"
        result = await self.execute(task, mode=mode)
        
        self._evolution_history.append({
            "skill_name": skill_name,
            "mode": mode,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })
        
        return result
    
    def get_evolution_history(self) -> List[Dict]:
        """获取进化历史"""
        return self._evolution_history
    
    async def get_quality_metrics(self) -> Dict[str, Any]:
        """获取质量指标"""
        return self._quality_metrics
    
    async def close(self):
        """关闭连接"""
        if self._mcp_process:
            try:
                self._mcp_process.terminate()
                self._mcp_process.wait(timeout=5)
            except:
                pass
        self._connected = False