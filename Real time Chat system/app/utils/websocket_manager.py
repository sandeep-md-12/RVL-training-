from typing import Dict, Set
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        # room_id -> set of websockets
        self.room_connections: Dict[int, Set[WebSocket]] = {}
        # user_id -> websocket (private)
        self.private_connections: Dict[int, WebSocket] = {}

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


ws_manager = WebSocketManager()
