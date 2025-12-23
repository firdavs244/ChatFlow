"""
ChatFlow - User Model
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.chat import ChatMember
    from app.models.message import Message
    from app.models.notification import Notification


class UserStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"
    BUSY = "busy"


class User(Base):
    """User model for authentication and profile."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default=UserStatus.OFFLINE.value,
    )
    last_seen: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status_message: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Settings (JSON stored as text for simplicity)
    notification_settings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    privacy_settings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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
    chat_memberships: Mapped[List["ChatMember"]] = relationship(
        "ChatMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    @property
    def is_online(self) -> bool:
        return self.status == UserStatus.ONLINE.value

