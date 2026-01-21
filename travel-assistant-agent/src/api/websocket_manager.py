import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from ..utils.logger import app_logger

class WebSocketManager:
    def __init__(self):
        # connection_id -> websocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, connection_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        app_logger.info(f"WebSocket connected: {connection_id}")

    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            app_logger.info(f"WebSocket disconnected: {connection_id}")

    async def send_message(self, connection_id: str, message: Dict[str, Any]):
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                app_logger.error(f"Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)

    async def broadcast_progress(self, connection_id: str, action: str, data: Dict[str, Any]):
        message = {
            "type": "progress",
            "action": action,
            "status": data.get("status"),
            "progress": data.get("progress", 0),
            "message": data.get("message", ""),
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_message(connection_id, message)

    async def send_intermediate_result(self, connection_id: str, action: str, data: Dict[str, Any]):
        message = {
            "type": "intermediate",
            "action": action,
            "data": data.get("data"),
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_message(connection_id, message)

    async def send_completion(self, connection_id: str, action: str, data: Dict[str, Any], duration_ms: float):
        message = {
            "type": "complete",
            "action": action,
            "data": data,
            "duration_ms": duration_ms,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_message(connection_id, message)

    async def send_error(self, connection_id: str, action: str, error: str, code: str = "INTERNAL_ERROR"):
        message = {
            "type": "error",
            "action": action,
            "error": error,
            "code": code,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_message(connection_id, message)

# Global manager instance
ws_manager = WebSocketManager()
