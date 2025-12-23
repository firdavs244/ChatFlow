"""
ChatFlow - WebSocket Router
"""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.core.redis import redis_manager
from app.core.security import verify_token
from app.models.chat import ChatMember
from app.models.user import User
from app.schemas.websocket import WSError, WSEventType, WSMessage
from app.websocket.manager import connection_manager

router = APIRouter()


async def get_user_from_token(token: str) -> User | None:
    """Authenticate WebSocket connection using JWT token."""
    user_id = verify_token(token, "access")
    if not user_id:
        return None
    
    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()


async def get_user_chat_ids(user_id: str) -> list[str]:
    """Get all chat IDs for a user."""
    async with async_session_factory() as db:
        result = await db.execute(
            select(ChatMember.chat_id).where(
                ChatMember.user_id == user_id,
                ChatMember.is_active == True,
            )
        )
        return [str(row[0]) for row in result.fetchall()]


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time communication."""
    user: User | None = None
    
    try:
        # Get token from query params
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token")
            return
        
        # Authenticate user
        user = await get_user_from_token(token)
        if not user:
            await websocket.close(code=4001, reason="Invalid authentication token")
            return
        
        user_id = str(user.id)
        
        # Connect
        await connection_manager.connect(websocket, user_id)
        
        # Subscribe to all user's chats
        chat_ids = await get_user_chat_ids(user_id)
        for chat_id in chat_ids:
            await connection_manager.subscribe_to_chat(user_id, chat_id)
        
        # Send connection success message
        await websocket.send_json({
            "event": WSEventType.CONNECT.value,
            "data": {
                "user_id": user_id,
                "username": user.username,
                "chat_count": len(chat_ids),
            },
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                event_type = message.get("event")
                event_data = message.get("data", {})
                
                await handle_websocket_event(
                    websocket, user, event_type, event_data
                )
                
            except json.JSONDecodeError:
                await send_error(websocket, "INVALID_JSON", "Invalid JSON format")
            
    except WebSocketDisconnect:
        if user:
            await connection_manager.disconnect(websocket, str(user.id))
    except Exception as e:
        if user:
            await connection_manager.disconnect(websocket, str(user.id))
        try:
            await websocket.close(code=4000, reason=str(e))
        except:
            pass


async def handle_websocket_event(
    websocket: WebSocket,
    user: User,
    event_type: str,
    data: dict,
) -> None:
    """Handle incoming WebSocket events."""
    user_id = str(user.id)
    
    if event_type == WSEventType.PING.value:
        # Respond with pong
        await websocket.send_json({
            "event": WSEventType.PONG.value,
            "data": {},
            "timestamp": datetime.utcnow().isoformat(),
        })
        # Refresh online status
        await redis_manager.set_user_online(user_id)
    
    elif event_type == WSEventType.TYPING_START.value:
        chat_id = data.get("chat_id")
        if chat_id:
            await connection_manager.send_typing_status(
                chat_id, user_id, user.username, is_typing=True
            )
    
    elif event_type == WSEventType.TYPING_STOP.value:
        chat_id = data.get("chat_id")
        if chat_id:
            await connection_manager.send_typing_status(
                chat_id, user_id, user.username, is_typing=False
            )
    
    elif event_type == WSEventType.MESSAGE_READ.value:
        chat_id = data.get("chat_id")
        message_id = data.get("message_id")
        if chat_id and message_id:
            await connection_manager.send_read_receipt(chat_id, user_id, message_id)
    
    elif event_type == "subscribe":
        # Subscribe to additional chat
        chat_id = data.get("chat_id")
        if chat_id:
            # Verify membership
            async with async_session_factory() as db:
                result = await db.execute(
                    select(ChatMember).where(
                        ChatMember.chat_id == chat_id,
                        ChatMember.user_id == user_id,
                        ChatMember.is_active == True,
                    )
                )
                if result.scalar_one_or_none():
                    await connection_manager.subscribe_to_chat(user_id, chat_id)
    
    elif event_type == "unsubscribe":
        chat_id = data.get("chat_id")
        if chat_id:
            await connection_manager.unsubscribe_from_chat(user_id, chat_id)
    
    else:
        await send_error(websocket, "UNKNOWN_EVENT", f"Unknown event type: {event_type}")


async def send_error(
    websocket: WebSocket,
    code: str,
    message: str,
    details: dict = None,
) -> None:
    """Send error message to client."""
    error = WSError(code=code, message=message, details=details)
    await websocket.send_json({
        "event": WSEventType.ERROR.value,
        "data": error.model_dump(),
        "timestamp": datetime.utcnow().isoformat(),
    })

