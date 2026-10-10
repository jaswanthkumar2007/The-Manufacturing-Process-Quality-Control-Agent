"""
WebSocket connection manager for real-time sensor data streaming.
"""
import json
import logging
from fastapi import WebSocket
from typing import Optional

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts sensor updates."""

    def __init__(self):
        self._connections: dict[str, WebSocket] = {}   # session_id → ws

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self._connections[session_id] = websocket
        logger.info("WebSocket connected: %s (total: %d)", session_id, len(self._connections))

    def disconnect(self, session_id: str):
        self._connections.pop(session_id, None)
        logger.info("WebSocket disconnected: %s (total: %d)", session_id, len(self._connections))

    async def send(self, session_id: str, data: dict):
        ws = self._connections.get(session_id)
        if ws:
            try:
                await ws.send_text(json.dumps(data))
            except Exception as exc:
                logger.error("WebSocket send error (%s): %s", session_id, exc)
                self.disconnect(session_id)

    async def broadcast(self, data: dict):
        """Broadcast to all connected clients."""
        dead = []
        for sid, ws in self._connections.items():
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.append(sid)
        for sid in dead:
            self.disconnect(sid)

    @property
    def active_connections(self) -> int:
        return len(self._connections)


manager = ConnectionManager()
