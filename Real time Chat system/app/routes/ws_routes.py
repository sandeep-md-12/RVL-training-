from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.database import get_db
from app.utils.auth import decode_access_token
from app.utils.websocket_manager import ws_manager
from app.repositories.user_repository import UserRepository
from app.repositories.receipt_repository import ReceiptRepository
from app.repositories.room_member_repository import RoomMemberRepository
from app.repositories.user_room_state_repository import UserRoomStateRepository
from app.controllers.message_controller import MessageController
from app.controllers.room_controller import RoomController
from app.services.user_service import UserService
from app.repositories.message_repository import MessageRepository

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

    # set user online
    user.is_online = True
    await UserRepository(db).update(user)

    # register connection
    ws_manager.room_connections.setdefault(room_id, set()).add(websocket)

    # ── reconnect/resume: push missed messages ────────────────────────────
    state_repo = UserRoomStateRepository(db)
    last_read_id = await state_repo.get_last_read_message_id(user.id, room_id)
    if last_read_id:
        missed = await MessageController(db).get_missed_messages(room_id, last_read_id)
        if missed:
            await websocket.send_json({"type": "message_history", "messages": [
                {**m, "created_at": m["created_at"].isoformat()} for m in missed
            ]})

    # ── reset unread + mark read on join ─────────────────────────────────
    receipt_repo = ReceiptRepository(db)
    room_members = await RoomMemberRepository(db).get_by_room(room_id)

   
    msg_repo = MessageRepository(db)
    unread_msgs = await msg_repo.get_missed_messages(room_id, last_read_id or 0)
    for msg in unread_msgs:
        await receipt_repo.mark_read(msg.id, user.id)
    if unread_msgs:
        await state_repo.reset_unread(user.id, room_id, unread_msgs[-1].id)

    # broadcast presence online
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

                # mark delivered for all room members except sender
                receipt_repo = ReceiptRepository(db)
                for m in room_members:
                    if m.user_id != user.id:
                        await receipt_repo.mark_delivered(saved["id"], m.user_id)
                        await state_repo.increment_unread(m.user_id, room_id)

                delivered_to = await receipt_repo.get_delivered_user_ids(saved["id"])
                read_by = await receipt_repo.get_read_user_ids(saved["id"])

                payload = {
                    "type": "message",
                    "message_id": saved["id"],
                    "sender_id": user.id,
                    "username": user.username,
                    "content": saved["content"],
                    "created_at": saved["created_at"].isoformat(),
                    "delivered_to": delivered_to,
                    "read_by": read_by,
                }
                await ws_manager.broadcast_room(room_id, payload, exclude=websocket)

            elif event_type == "read":
                message_id = data.get("message_id")
                if message_id:
                    await receipt_repo.mark_read(message_id, user.id)
                    await state_repo.reset_unread(user.id, room_id, message_id)
                    read_by = await receipt_repo.get_read_user_ids(message_id)
                    await ws_manager.broadcast_room(room_id, {
                        "type": "read_receipt",
                        "message_id": message_id,
                        "read_by": read_by,
                    })

            elif event_type == "typing":
                is_typing = data.get("is_typing", False)
                await ws_manager.broadcast_room(room_id, {
                    "type": "typing",
                    "user_id": user.id,
                    "username": user.username,
                    "is_typing": is_typing,
                }, exclude=websocket)
                if is_typing:
                    ws_manager.schedule_typing_clear("room", room_id, user.id, user.username, exclude=websocket)
                else:
                    ws_manager.cancel_typing("room", room_id, user.id)

    except WebSocketDisconnect:
        ws_manager.disconnect_room(room_id, websocket)
        ws_manager.cancel_typing("room", room_id, user.id)

        # set offline + last_seen
        await UserService(db).set_offline(user.id)

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

    # set user online
    user.is_online = True
    await UserRepository(db).update(user)

    # register connection
    ws_manager.private_connections[user.id] = websocket

    # ── reconnect/resume: push missed private messages ────────────────────
    msg_repo = MessageRepository(db)
    receipt_repo = ReceiptRepository(db)
    missed = await msg_repo.get_private_messages(
        user_id=user.id, other_user_id=recipient_id, limit=50, cursor=None
    )
    unread = [m for m in missed if not any(
        r for r in [await receipt_repo.get(m.id, user.id)] if r and r.is_read
    )]
    if unread:
        await websocket.send_json({"type": "message_history", "messages": [
            {
                "message_id": m.id,
                "sender_id": m.sender_id,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
            } for m in unread
        ]})
        for m in unread:
            await receipt_repo.mark_delivered(m.id, user.id)

    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            if event_type == "message":
                content = data.get("content", "").strip()
                if not content:
                    continue
                saved = await MessageController(db).save_private_message(user.id, recipient_id, content)

                receipt_repo = ReceiptRepository(db)
                # mark delivered if recipient is online
                if ws_manager.is_online(recipient_id):
                    await receipt_repo.mark_delivered(saved["id"], recipient_id)

                delivered_to = await receipt_repo.get_delivered_user_ids(saved["id"])
                read_by = await receipt_repo.get_read_user_ids(saved["id"])

                payload = {
                    "type": "message",
                    "message_id": saved["id"],
                    "sender_id": user.id,
                    "username": user.username,
                    "content": saved["content"],
                    "created_at": saved["created_at"].isoformat(),
                    "delivered_to": delivered_to,
                    "read_by": read_by,
                }
                await ws_manager.send_private(recipient_id, payload)

                # auto mark read when recipient receives it
                if ws_manager.is_online(recipient_id):
                    await receipt_repo.mark_read(saved["id"], recipient_id)
                    read_by = await receipt_repo.get_read_user_ids(saved["id"])
                    payload["read_by"] = read_by

            elif event_type == "read":
                message_id = data.get("message_id")
                if message_id:
                    receipt_repo = ReceiptRepository(db)
                    await receipt_repo.mark_read(message_id, user.id)
                    read_by = await receipt_repo.get_read_user_ids(message_id)
                    await ws_manager.send_private(user.id, {
                        "type": "read_receipt",
                        "message_id": message_id,
                        "read_by": read_by,
                    })

            elif event_type == "typing":
                is_typing = data.get("is_typing", False)
                await ws_manager.send_private(recipient_id, {
                    "type": "typing",
                    "user_id": user.id,
                    "username": user.username,
                    "is_typing": is_typing,
                })
                if is_typing:
                    ws_manager.schedule_typing_clear("private", recipient_id, user.id, user.username)
                else:
                    ws_manager.cancel_typing("private", recipient_id, user.id)

    except WebSocketDisconnect:
        ws_manager.disconnect_private(user.id)
        ws_manager.cancel_typing("private", recipient_id, user.id)
        await UserService(db).set_offline(user.id)
