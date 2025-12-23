"""
ChatFlow - Notification Model
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class NotificationType(str, Enum):
    MESSAGE = "message"
    MENTION = "mention"
    REACTION = "reaction"
    GROUP_INVITE = "group_invite"
    GROUP_UPDATE = "group_update"
    FRIEND_REQUEST = "friend_request"
    SYSTEM = "system"


class Notification(Base):
    """Notification model for push notifications and in-app notifications."""

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    
    # Notification content
    notification_type: Mapped[str] = mapped_column(
        String(50),
        default=NotificationType.MESSAGE.value,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Related entities
    chat_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    message_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    sender_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    
    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Action URL
    action_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Additional data (JSON as text)
    data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification {self.id} for {self.user_id}>"

