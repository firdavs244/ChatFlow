"""
ChatFlow - Chat Schemas
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.chat import ChatType, MemberRole
from app.schemas.user import UserProfile


class ChatCreate(BaseModel):
    """Schema for creating a new chat."""
    
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    chat_type: ChatType = ChatType.PRIVATE
    member_ids: List[UUID] = Field(default_factory=list)
    avatar_url: Optional[str] = None


class ChatUpdate(BaseModel):
    """Schema for updating a chat."""
    
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    is_muted: Optional[bool] = None
    only_admins_can_post: Optional[bool] = None


class ChatMemberResponse(BaseModel):
    """Schema for chat member response."""
    
    id: UUID
    user_id: UUID
    role: str
    nickname: Optional[str] = None
    is_active: bool
    joined_at: datetime
    user: Optional[UserProfile] = None

    class Config:
        from_attributes = True


class LastMessagePreview(BaseModel):
    """Schema for last message preview in chat list."""
    
    id: UUID
    content: Optional[str] = None
    message_type: str
    sender_id: Optional[UUID] = None
    sender_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Schema for chat response."""
    
    id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    chat_type: str
    is_active: bool
    invite_link: Optional[str] = None
    last_message_at: Optional[datetime] = None
    created_at: datetime
    members: List[ChatMemberResponse] = []
    member_count: int = 0

    class Config:
        from_attributes = True


class ChatListResponse(BaseModel):
    """Schema for chat list item (optimized for list view)."""
    
    id: UUID
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    chat_type: str
    is_muted: bool = False
    is_pinned: bool = False
    unread_count: int = 0
    last_message: Optional[LastMessagePreview] = None
    last_message_at: Optional[datetime] = None
    # For private chats
    other_user: Optional[UserProfile] = None
    # Online status (for private chats)
    is_online: bool = False

    class Config:
        from_attributes = True


class ChatMemberAdd(BaseModel):
    """Schema for adding members to a chat."""
    
    user_ids: List[UUID]
    role: MemberRole = MemberRole.MEMBER


class ChatMemberUpdate(BaseModel):
    """Schema for updating a chat member."""
    
    role: Optional[MemberRole] = None
    nickname: Optional[str] = Field(None, max_length=50)
    is_muted: Optional[bool] = None
    notifications_enabled: Optional[bool] = None


class TypingStatus(BaseModel):
    """Schema for typing status."""
    
    chat_id: UUID
    user_id: UUID
    username: str
    is_typing: bool = True


class ChatInviteLink(BaseModel):
    """Schema for chat invite link."""
    
    chat_id: UUID
    invite_link: str
    expires_at: Optional[datetime] = None

