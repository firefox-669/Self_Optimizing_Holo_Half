import asyncio
import aiohttp
import json
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime


class OpenHandsExecutor:
    """
    OpenHands 执行器 - 真实集成远程OpenHands服务
    """

    def __init__(self, base_url: str = "http://localhost:3000", workspace: str = None):
        self.base_url = base_url.rstrip("/")
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.session: Optional[aiohttp.ClientSession] = None
        self._conversation_history: List[Dict] = []
        self._connected = False
        self._agent_id: Optional[str] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def connect(self) -> bool:
        """连接到OpenHands服务"""
        session = await self._get_session()
        try:
            async with session.get(
                f"{self.base_url}/api/status",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    self._connected = True
                    return True
        except Exception:
            pass
        self._connected = False
        return False

    async def execute(
        self,
        task: str,
        workspace: Path,
        max_iterations: int = 20,
    ) -> Dict[str, Any]:
        """
        通过OpenHands API执行任务
        """
        if not self._connected:
            await self.connect()

        if not self._connected:
            return {
                "success": False,
                "error": "OpenHands not connected",
                "fallback": False,
            }

        session = await self._get_session()
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        payload = {
            "conversation_id": conversation_id,
            "message": task,
            "max_iterations": max_iterations,
            "workspace": str(workspace),
        }

        try:
            async with session.post(
                f"{self.base_url}/api/execute",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=600),
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                else:
                    error_text = await resp.text()
                    return {
                        "success": False,
                        "error": f"HTTP {resp.status}: {error_text}",
                        "fallback": False,
                    }
        except aiohttp.ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "fallback": False,
            }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Timeout",
                "fallback": False,
            }

        execution_record = {
            "id": conversation_id,
            "task": task,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
        self._conversation_history.append(execution_record)

        return {
            "success": True,
            "conversation_id": conversation_id,
            "output": result.get("output", ""),
            "actions": result.get("actions", []),
            "artifacts": result.get("artifacts", []),
            "response": result.get("response", ""),
        }

    async def execute_with_history(
        self,
        task: str,
        workspace: Path,
        context: Optional[Dict[str, Any]] = None,
        max_iterations: int = 20,
    ) -> Dict[str, Any]:
        """带记忆的执行"""
        return await self.execute(task, workspace, max_iterations)

    def get_history(self) -> List[Dict]:
        return self._conversation_history

    def clear_history(self):
        self._conversation_history = []

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
