"""
ChatFlow - WebSocket Event Schemas
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class WSEventType(str, Enum):
    """WebSocket event types."""
    
    # Connection
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"
    
    # Messages
    MESSAGE_NEW = "message.new"
    MESSAGE_UPDATE = "message.update"
    MESSAGE_DELETE = "message.delete"
    MESSAGE_REACTION = "message.reaction"
    MESSAGE_READ = "message.read"
    
    # Typing
    TYPING_START = "typing.start"
    TYPING_STOP = "typing.stop"
    
    # User status
    USER_ONLINE = "user.online"
    USER_OFFLINE = "user.offline"
    USER_STATUS = "user.status"
    
    # Chat
    CHAT_NEW = "chat.new"
    CHAT_UPDATE = "chat.update"
    CHAT_DELETE = "chat.delete"
    CHAT_MEMBER_JOIN = "chat.member.join"
    CHAT_MEMBER_LEAVE = "chat.member.leave"
    
    # Notifications
    NOTIFICATION = "notification"
    
    # Errors
    ERROR = "error"


class WSMessage(BaseModel):
    """WebSocket message wrapper."""
    
    event: WSEventType
    data: Any
    timestamp: datetime = None
    
    def __init__(self, **data):
        if "timestamp" not in data or data["timestamp"] is None:
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)


class WSError(BaseModel):
    """WebSocket error message."""
    
    code: str
    message: str
    details: Optional[dict] = None


class WSNewMessage(BaseModel):
    """WebSocket new message event data."""
    
    id: UUID
    chat_id: UUID
    sender_id: Optional[UUID]
    sender_name: Optional[str]
    sender_avatar: Optional[str]
    content: Optional[str]
    message_type: str
    reply_to_id: Optional[UUID] = None
    attachments: list = []
    created_at: datetime


class WSMessageUpdate(BaseModel):
    """WebSocket message update event data."""
    
    id: UUID
    chat_id: UUID
    content: Optional[str]
    is_edited: bool
    edited_at: Optional[datetime]


class WSMessageDelete(BaseModel):
    """WebSocket message delete event data."""
    
    id: UUID
    chat_id: UUID
    deleted_for_everyone: bool


class WSMessageReaction(BaseModel):
    """WebSocket message reaction event data."""
    
    message_id: UUID
    chat_id: UUID
    user_id: UUID
    emoji: str
    action: str  # "add" or "remove"


class WSMessageRead(BaseModel):
    """WebSocket message read event data."""
    
    chat_id: UUID
    user_id: UUID
    message_id: UUID
    read_at: datetime


class WSTyping(BaseModel):
    """WebSocket typing event data."""
    
    chat_id: UUID
    user_id: UUID
    username: str


class WSUserStatus(BaseModel):
    """WebSocket user status event data."""
    
    user_id: UUID
    status: str
    last_seen: Optional[datetime] = None


class WSChatUpdate(BaseModel):
    """WebSocket chat update event data."""
    
    chat_id: UUID
    name: Optional[str]
    avatar_url: Optional[str]
    updated_by: UUID


class WSMemberUpdate(BaseModel):
    """WebSocket chat member update event data."""
    
    chat_id: UUID
    user_id: UUID
    username: str
    action: str  # "join" or "leave"

