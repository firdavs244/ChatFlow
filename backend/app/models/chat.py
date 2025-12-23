"""
ChatFlow - Chat & ChatMember Models
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.message import Message


class ChatType(str, Enum):
    PRIVATE = "private"  # 1-to-1 chat
    GROUP = "group"      # Group chat
    CHANNEL = "channel"  # Broadcast channel


class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class Chat(Base):
    """Chat room model (supports private, group, and channel types)."""

    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Chat info
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Type
    chat_type: Mapped[str] = mapped_column(
        String(20),
        default=ChatType.PRIVATE.value,
        index=True,
    )
    
    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_muted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # For groups/channels
    invite_link: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
    )
    max_members: Mapped[int] = mapped_column(Integer, default=1000)
    
    # Message settings
    allow_messages: Mapped[bool] = mapped_column(Boolean, default=True)
    only_admins_can_post: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Last message info (for sorting chats)
    last_message_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    last_message_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    members: Mapped[List["ChatMember"]] = relationship(
        "ChatMember",
        back_populates="chat",
        cascade="all, delete-orphan",
    )
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Chat {self.id} ({self.chat_type})>"

    @property
    def is_private(self) -> bool:
        return self.chat_type == ChatType.PRIVATE.value

    @property
    def is_group(self) -> bool:
        return self.chat_type == ChatType.GROUP.value

    @property
    def is_channel(self) -> bool:
        return self.chat_type == ChatType.CHANNEL.value


class ChatMember(Base):
    """Chat membership model."""

    __tablename__ = "chat_members"

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
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    
    # Role
    role: Mapped[str] = mapped_column(
        String(20),
        default=MemberRole.MEMBER.value,
    )
    
    # Nickname in this chat
    nickname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_muted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Notification settings
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    muted_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Read status
    last_read_message_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    last_read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    unread_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="chat_memberships")

    def __repr__(self) -> str:
        return f"<ChatMember {self.user_id} in {self.chat_id}>"

    @property
    def is_admin(self) -> bool:
        return self.role in [MemberRole.OWNER.value, MemberRole.ADMIN.value]

    @property
    def is_owner(self) -> bool:
        return self.role == MemberRole.OWNER.value

