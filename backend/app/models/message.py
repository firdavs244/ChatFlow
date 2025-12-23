"""
ChatFlow - Message Models
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.chat import Chat


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    VOICE = "voice"
    STICKER = "sticker"
    GIF = "gif"
    LOCATION = "location"
    CONTACT = "contact"
    SYSTEM = "system"  # System messages (user joined, left, etc.)


class MessageStatus(str, Enum):
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Message(Base):
    """Message model."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Foreign keys
    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        index=True,
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Message content
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_type: Mapped[str] = mapped_column(
        String(20),
        default=MessageType.TEXT.value,
    )
    
    # Reply to
    reply_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Forward from
    forwarded_from_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
    )
    forwarded_from_chat_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default=MessageStatus.SENT.value,
    )
    
    # Editing
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    edited_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Deletion
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    deleted_for_everyone: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Pinned
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    pinned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Extra data (JSON as text)
    extra_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
    sender: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="messages",
    )
    reply_to: Mapped[Optional["Message"]] = relationship(
        "Message",
        remote_side="Message.id",
        foreign_keys=[reply_to_id],
    )
    reactions: Mapped[List["MessageReaction"]] = relationship(
        "MessageReaction",
        back_populates="message",
        cascade="all, delete-orphan",
    )
    attachments: Mapped[List["MessageAttachment"]] = relationship(
        "MessageAttachment",
        back_populates="message",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Message {self.id} in {self.chat_id}>"


class MessageReaction(Base):
    """Message reaction model (emoji reactions)."""

    __tablename__ = "message_reactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    
    emoji: Mapped[str] = mapped_column(String(20), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    message: Mapped["Message"] = relationship("Message", back_populates="reactions")

    def __repr__(self) -> str:
        return f"<MessageReaction {self.emoji} on {self.message_id}>"


class MessageAttachment(Base):
    """Message attachment model (files, images, etc.)."""

    __tablename__ = "message_attachments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        index=True,
    )
    
    # File info
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # in bytes
    
    # For images/videos
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # in seconds
    
    # Thumbnail
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Extra data (JSON)
    extra_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    message: Mapped["Message"] = relationship("Message", back_populates="attachments")

    def __repr__(self) -> str:
        return f"<MessageAttachment {self.file_name}>"

