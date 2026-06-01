from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.database import get_db
from app.utils.auth import decode_access_token
from app.utils.websocket_manager import ws_manager
from app.repositories.user_repository import UserRepository
from app.controllers.message_controller import MessageController
from app.controllers.room_controller import RoomController

router = APIRouter(tags=["WebSocket"])


async def _authenticate_ws(websocket: WebSocket, db: AsyncSession):
    """Accepts connection, waits for auth message, returns user or closes."""
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        if data.get("type") != "auth":
            await websocket.close(code=4001, reason="First message must be auth")
            return None
        payload = decode_access_token(data.get("token", ""))
        if not payload:
            await websocket.close(code=4001, reason="Invalid token")
            return None
        user = await UserRepository(db).get_by_id(int(payload["sub"]))
        if not user or not user.is_active:
            await websocket.close(code=4001, reason="Unauthorized")
            return None
        return user
    except Exception:
        await websocket.close(code=4001, reason="Auth failed")
        return None


@router.websocket("/ws/chat/{room_id}")
async def room_chat(room_id: int, websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    user = await _authenticate_ws(websocket, db)
    if not user:
        return

    # verify membership
    if not await RoomController(db).is_member(room_id, user.id):
        await websocket.send_json({"type": "error", "detail": "You are not a member of this room"})
        await websocket.close(code=4003)
        return

    # register without re-accepting (already accepted in _authenticate_ws)
    ws_manager.room_connections.setdefault(room_id, set()).add(websocket)
    await ws_manager.broadcast_room(room_id, {
        "type": "presence",
        "user_id": user.id,
        "username": user.username,
        "status": "online",
    }, exclude=websocket)

    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            if event_type == "message":
                content = data.get("content", "").strip()
                if not content:
                    continue
                saved = await MessageController(db).save_room_message(user.id, room_id, content)
                await ws_manager.broadcast_room(room_id, {
                    "type": "message",
                    "message_id": saved["id"],
                    "sender_id": user.id,
                    "username": user.username,
                    "content": saved["content"],
                    "created_at": saved["created_at"].isoformat(),
                }, exclude=websocket)

            elif event_type == "typing":
                await ws_manager.broadcast_room(room_id, {
                    "type": "typing",
                    "user_id": user.id,
                    "username": user.username,
                    "is_typing": data.get("is_typing", False),
                }, exclude=websocket)

    except WebSocketDisconnect:
        ws_manager.disconnect_room(room_id, websocket)
        await ws_manager.broadcast_room(room_id, {
            "type": "presence",
            "user_id": user.id,
            "username": user.username,
            "status": "offline",
        })


@router.websocket("/ws/private/{recipient_id}")
async def private_chat(recipient_id: int, websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    user = await _authenticate_ws(websocket, db)
    if not user:
        return

    # register without re-accepting
    ws_manager.private_connections[user.id] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            if event_type == "message":
                content = data.get("content", "").strip() 
                if not content:
                    continue
                saved = await MessageController(db).save_private_message(user.id, recipient_id, content)
                payload = {
                    "type": "message",
                    "message_id": saved["id"],
                    "sender_id": user.id,
                    "username": user.username,
                    "content": saved["content"],
                    "created_at": saved["created_at"].isoformat(),
                } 
                # deliver to recipient if online
                await ws_manager.send_private(recipient_id, payload)

            elif event_type == "typing":
                await ws_manager.send_private(recipient_id, {
                    "type": "typing",
                    "user_id": user.id,
                    "username": user.username,
                    "is_typing": data.get("is_typing", False),
                })

    except WebSocketDisconnect:
        ws_manager.disconnect_private(user.id)
