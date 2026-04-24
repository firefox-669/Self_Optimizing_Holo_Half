"""
OpenHands 客户端
提供 OpenHands 服务的 Python 接口
"""

import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime


class OpenHandsClient:
    """
    OpenHands 客户端
    用于与 OpenHands 服务交互
    """
    
    def __init__(
        self, 
        workspace: str = None,
        base_url: str = "http://localhost:3000",
        config_path: str = None
    ):
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.base_url = base_url
        self.config_path = config_path
        self._connected = False
        self._runtime = None
        self._session_history: List[Dict] = []
    
    async def connect(self) -> bool:
        """连接到 OpenHands 服务"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/status",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        self._connected = True
                        return True
        except Exception:
            pass
        
        return await self._connect_sdk()
    
    async def _connect_sdk(self) -> bool:
        """通过 SDK 连接"""
        try:
            from openhands import runtime as oh_runtime
            
            self._runtime = oh_runtime.OpenHandsRuntime(
                workspace=str(self.workspace)
            )
            self._connected = True
            return True
        except ImportError:
            pass
        except Exception:
            pass
        
        self._connected = False
        return False
    
    async def execute(
        self, 
        instruction: str, 
        max_iterations: int = 20,
        **kwargs
    ) -> Dict[str, Any]:
        """执行任务"""
        if not self._connected:
            await self.connect()
        
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 使用 SDK 执行
        if self._runtime:
            try:
                result = await self._runtime.run(
                    instruction=instruction,
                    max_iterations=max_iterations,
                    **kwargs
                )
                
                self._session_history.append({
                    "session_id": session_id,
                    "instruction": instruction,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                })
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "output": result.get("output", ""),
                    "actions": result.get("actions", []),
                    "artifacts": result.get("artifacts", []),
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "session_id": session_id,
                }
        
        return {
            "success": False,
            "error": "Not connected",
            "session_id": session_id,
        }
    
    async def execute_with_history(
        self, 
        instruction: str,
        context: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """带上下文的执行"""
        if context:
            full_instruction = f"{context.get('system_prompt', '')}\n\nTask: {instruction}"
        else:
            full_instruction = instruction
        
        return await self.execute(full_instruction, **kwargs)
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._connected
    
    def get_history(self) -> List[Dict]:
        """获取执行历史"""
        return self._session_history
    
    async def close(self):
        """关闭连接"""
        if self._runtime:
            try:
                await self._runtime.close()
            except:
                pass
        self._connected = False
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        return False