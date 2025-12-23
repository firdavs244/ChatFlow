"""
ChatFlow - Message Schemas
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.message import MessageType, MessageStatus
from app.schemas.user import UserProfile


class AttachmentCreate(BaseModel):
    """Schema for creating an attachment."""
    
    file_name: str
    file_url: str
    file_type: str
    file_size: int
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    thumbnail_url: Optional[str] = None


class AttachmentResponse(BaseModel):
    """Schema for attachment response."""
    
    id: UUID
    file_name: str
    file_url: str
    file_type: str
    file_size: int
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MessageReactionResponse(BaseModel):
    """Schema for message reaction response."""
    
    id: UUID
    user_id: UUID
    emoji: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReactionSummary(BaseModel):
    """Schema for reaction summary (grouped by emoji)."""
    
    emoji: str
    count: int
    users: List[UUID] = []
    has_reacted: bool = False  # Current user has reacted


class MessageCreate(BaseModel):
    """Schema for creating a new message."""
    
    chat_id: UUID
    content: Optional[str] = Field(None, max_length=10000)
    message_type: MessageType = MessageType.TEXT
    reply_to_id: Optional[UUID] = None
    forwarded_from_id: Optional[UUID] = None
    attachments: List[AttachmentCreate] = []
    metadata: Optional[dict] = None


class MessageUpdate(BaseModel):
    """Schema for updating a message."""
    
    content: str = Field(..., max_length=10000)


class ReplyPreview(BaseModel):
    """Schema for reply message preview."""
    
    id: UUID
    content: Optional[str] = None
    message_type: str
    sender: Optional[UserProfile] = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema for message response."""
    
    id: UUID
    chat_id: UUID
    sender_id: Optional[UUID] = None
    sender: Optional[UserProfile] = None
    content: Optional[str] = None
    message_type: str
    status: str
    reply_to: Optional[ReplyPreview] = None
    forwarded_from_id: Optional[UUID] = None
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    is_deleted: bool = False
    is_pinned: bool = False
    attachments: List[AttachmentResponse] = []
    reactions: List[ReactionSummary] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageReactionCreate(BaseModel):
    """Schema for adding a reaction."""
    
    emoji: str = Field(..., max_length=20)


class MessageList(BaseModel):
    """Schema for paginated message list."""
    
    messages: List[MessageResponse]
    total: int
    has_more: bool
    next_cursor: Optional[str] = None


class MessageDelete(BaseModel):
    """Schema for deleting a message."""
    
    delete_for_everyone: bool = False


class MessageSearch(BaseModel):
    """Schema for searching messages."""
    
    query: str = Field(..., min_length=1, max_length=200)
    chat_id: Optional[UUID] = None
    sender_id: Optional[UUID] = None
    message_type: Optional[MessageType] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ReadReceipt(BaseModel):
    """Schema for read receipt."""
    
    chat_id: UUID
    message_id: UUID
    read_at: datetime

