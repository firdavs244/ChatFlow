"""
ChatFlow - WebSocket Connection Manager
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import UUID

from fastapi import WebSocket

from app.core.redis import redis_manager
from app.schemas.websocket import WSEventType, WSMessage


class ConnectionManager:
    """Manages WebSocket connections for real-time messaging."""

    def __init__(self):
        # user_id -> list of websockets (supports multiple devices)
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # chat_id -> set of user_ids
        self.chat_subscriptions: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        
        # Set user online in Redis
        await redis_manager.set_user_online(user_id)
        
        # Notify other users that this user is online
        await self.broadcast_user_status(user_id, "online")

    async def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Handle WebSocket disconnection."""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # If no more connections, user is offline
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                await redis_manager.set_user_offline(user_id)
                await self.broadcast_user_status(user_id, "offline")

    async def subscribe_to_chat(self, user_id: str, chat_id: str) -> None:
        """Subscribe a user to a chat's real-time updates."""
        if chat_id not in self.chat_subscriptions:
            self.chat_subscriptions[chat_id] = set()
        self.chat_subscriptions[chat_id].add(user_id)

    async def unsubscribe_from_chat(self, user_id: str, chat_id: str) -> None:
        """Unsubscribe a user from a chat's updates."""
        if chat_id in self.chat_subscriptions:
            self.chat_subscriptions[chat_id].discard(user_id)

    async def send_personal_message(
        self,
        user_id: str,
        event: WSEventType,
        data: dict,
    ) -> None:
        """Send a message to a specific user (all their devices)."""
        message = WSMessage(event=event, data=data, timestamp=datetime.utcnow())
        message_json = message.model_dump_json()
        
        if user_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(message_json)
                except Exception:
                    disconnected.append(websocket)
            
            # Clean up disconnected sockets
            for ws in disconnected:
                await self.disconnect(ws, user_id)

    async def broadcast_to_chat(
        self,
        chat_id: str,
        event: WSEventType,
        data: dict,
        exclude_user: Optional[str] = None,
    ) -> None:
        """Broadcast a message to all users in a chat."""
        if chat_id not in self.chat_subscriptions:
            return
        
        message = WSMessage(event=event, data=data, timestamp=datetime.utcnow())
        message_json = message.model_dump_json()
        
        for user_id in self.chat_subscriptions[chat_id]:
            if exclude_user and user_id == exclude_user:
                continue
            
            if user_id in self.active_connections:
                disconnected = []
                for websocket in self.active_connections[user_id]:
                    try:
                        await websocket.send_text(message_json)
                    except Exception:
                        disconnected.append(websocket)
                
                for ws in disconnected:
                    await self.disconnect(ws, user_id)

    async def broadcast_user_status(
        self,
        user_id: str,
        status: str,
    ) -> None:
        """Broadcast user online/offline status to relevant users."""
        from app.schemas.websocket import WSUserStatus
        
        event = WSEventType.USER_ONLINE if status == "online" else WSEventType.USER_OFFLINE
        data = WSUserStatus(
            user_id=UUID(user_id),
            status=status,
            last_seen=datetime.utcnow() if status == "offline" else None,
        )
        
        # Broadcast to all chats the user is part of
        for chat_id, users in self.chat_subscriptions.items():
            if user_id in users:
                await self.broadcast_to_chat(
                    chat_id,
                    event,
                    data.model_dump(mode="json"),
                    exclude_user=user_id,
                )

    async def send_typing_status(
        self,
        chat_id: str,
        user_id: str,
        username: str,
        is_typing: bool = True,
    ) -> None:
        """Send typing status to chat members."""
        from app.schemas.websocket import WSTyping
        
        event = WSEventType.TYPING_START if is_typing else WSEventType.TYPING_STOP
        data = WSTyping(
            chat_id=UUID(chat_id),
            user_id=UUID(user_id),
            username=username,
        )
        
        await self.broadcast_to_chat(
            chat_id,
            event,
            data.model_dump(mode="json"),
            exclude_user=user_id,
        )
        
        # Also update Redis for typing status
        await redis_manager.set_user_typing(user_id, chat_id, is_typing)

    async def send_new_message(
        self,
        chat_id: str,
        message_data: dict,
        sender_id: str,
    ) -> None:
        """Send new message notification to chat members."""
        await self.broadcast_to_chat(
            chat_id,
            WSEventType.MESSAGE_NEW,
            message_data,
            exclude_user=sender_id,  # Don't send to sender
        )

    async def send_message_update(
        self,
        chat_id: str,
        message_id: str,
        content: str,
        is_edited: bool,
        edited_at: datetime,
    ) -> None:
        """Send message update notification."""
        from app.schemas.websocket import WSMessageUpdate
        
        data = WSMessageUpdate(
            id=UUID(message_id),
            chat_id=UUID(chat_id),
            content=content,
            is_edited=is_edited,
            edited_at=edited_at,
        )
        
        await self.broadcast_to_chat(
            chat_id,
            WSEventType.MESSAGE_UPDATE,
            data.model_dump(mode="json"),
        )

    async def send_message_delete(
        self,
        chat_id: str,
        message_id: str,
        deleted_for_everyone: bool,
    ) -> None:
        """Send message delete notification."""
        from app.schemas.websocket import WSMessageDelete
        
        data = WSMessageDelete(
            id=UUID(message_id),
            chat_id=UUID(chat_id),
            deleted_for_everyone=deleted_for_everyone,
        )
        
        await self.broadcast_to_chat(
            chat_id,
            WSEventType.MESSAGE_DELETE,
            data.model_dump(mode="json"),
        )

    async def send_read_receipt(
        self,
        chat_id: str,
        user_id: str,
        message_id: str,
    ) -> None:
        """Send read receipt notification."""
        from app.schemas.websocket import WSMessageRead
        
        data = WSMessageRead(
            chat_id=UUID(chat_id),
            user_id=UUID(user_id),
            message_id=UUID(message_id),
            read_at=datetime.utcnow(),
        )
        
        await self.broadcast_to_chat(
            chat_id,
            WSEventType.MESSAGE_READ,
            data.model_dump(mode="json"),
            exclude_user=user_id,
        )

    def get_online_users_count(self) -> int:
        """Get total number of online users."""
        return len(self.active_connections)

    def is_user_online(self, user_id: str) -> bool:
        """Check if a user is currently online."""
        return user_id in self.active_connections


# Global connection manager instance
connection_manager = ConnectionManager()

