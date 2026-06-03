from typing import Dict, Set
import asyncio
from fastapi import WebSocket

TYPING_TIMEOUT = 5  # seconds


class WebSocketManager:
    def __init__(self):
        # room_id -> set of websockets
        self.room_connections: Dict[int, Set[WebSocket]] = {}
        # user_id -> websocket (private)
        self.private_connections: Dict[int, WebSocket] = {}
        # (context, user_id) -> asyncio.Task for typing timeout
        self._typing_timers: Dict[tuple, asyncio.Task] = {}

    # ── Room ────────────────────────────────────────────────────────────────

    def disconnect_room(self, room_id: int, websocket: WebSocket):
        if room_id in self.room_connections:
            self.room_connections[room_id].discard(websocket)
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]

    async def broadcast_room(self, room_id: int, payload: dict, exclude: WebSocket = None):
        for ws in list(self.room_connections.get(room_id, [])):
            if ws is exclude:
                continue
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect_room(room_id, ws)

    # ── Private ─────────────────────────────────────────────────────────────

    def disconnect_private(self, user_id: int):
        self.private_connections.pop(user_id, None)

    async def send_private(self, recipient_id: int, payload: dict) -> bool:
        ws = self.private_connections.get(recipient_id)
        if ws:
            try:
                await ws.send_json(payload)
                return True
            except Exception:
                self.disconnect_private(recipient_id)
        return False

    def is_online(self, user_id: int) -> bool:
        return user_id in self.private_connections

    # ── Typing Timeout ───────────────────────────────────────────────────────

    def _cancel_typing_timer(self, key: tuple):
        task = self._typing_timers.pop(key, None)
        if task:
            task.cancel()

    def schedule_typing_clear(self, context: str, context_id: int, user_id: int, username: str, exclude: WebSocket = None):
        key = (context, context_id, user_id)
        self._cancel_typing_timer(key)

        async def _clear():
            await asyncio.sleep(TYPING_TIMEOUT)
            payload = {"type": "typing", "user_id": user_id, "username": username, "is_typing": False}
            if context == "room":
                await self.broadcast_room(context_id, payload, exclude=exclude)
            else:
                await self.send_private(context_id, payload)
            self._typing_timers.pop(key, None)

        self._typing_timers[key] = asyncio.ensure_future(_clear())

    def cancel_typing(self, context: str, context_id: int, user_id: int):
        self._cancel_typing_timer((context, context_id, user_id))


ws_manager = WebSocketManager()
