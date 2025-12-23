"""
ChatFlow - Messages Router
"""

from datetime import datetime
from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.redis import RedisManager, get_redis
from app.models.chat import Chat, ChatMember
from app.models.message import Message, MessageAttachment, MessageReaction, MessageStatus
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.message import (
    AttachmentResponse,
    MessageCreate,
    MessageDelete,
    MessageList,
    MessageReactionCreate,
    MessageResponse,
    MessageUpdate,
    ReactionSummary,
    ReplyPreview,
)
from app.schemas.user import UserProfile

router = APIRouter()


async def get_message_response(message: Message, current_user: User, db: AsyncSession) -> MessageResponse:
    """Build message response with all related data."""
    # Get sender profile
    sender = None
    if message.sender:
        sender = UserProfile.model_validate(message.sender)
    
    # Get reply preview
    reply_to = None
    if message.reply_to_id:
        reply_result = await db.execute(
            select(Message)
            .options(selectinload(Message.sender))
            .where(Message.id == message.reply_to_id)
        )
        reply_message = reply_result.scalar_one_or_none()
        if reply_message:
            reply_to = ReplyPreview(
                id=reply_message.id,
                content=reply_message.content[:100] if reply_message.content else None,
                message_type=reply_message.message_type,
                sender=UserProfile.model_validate(reply_message.sender) if reply_message.sender else None,
            )
    
    # Get attachments
    attachments = [
        AttachmentResponse.model_validate(a) for a in message.attachments
    ]
    
    # Get reactions grouped by emoji
    reactions_dict = {}
    for reaction in message.reactions:
        if reaction.emoji not in reactions_dict:
            reactions_dict[reaction.emoji] = ReactionSummary(
                emoji=reaction.emoji,
                count=0,
                users=[],
                has_reacted=False,
            )
        reactions_dict[reaction.emoji].count += 1
        reactions_dict[reaction.emoji].users.append(reaction.user_id)
        if reaction.user_id == current_user.id:
            reactions_dict[reaction.emoji].has_reacted = True
    
    return MessageResponse(
        id=message.id,
        chat_id=message.chat_id,
        sender_id=message.sender_id,
        sender=sender,
        content=message.content,
        message_type=message.message_type,
        status=message.status,
        reply_to=reply_to,
        forwarded_from_id=message.forwarded_from_id,
        is_edited=message.is_edited,
        edited_at=message.edited_at,
        is_deleted=message.is_deleted,
        is_pinned=message.is_pinned,
        attachments=attachments,
        reactions=list(reactions_dict.values()),
        created_at=message.created_at,
        updated_at=message.updated_at,
    )


@router.get("/chat/{chat_id}", response_model=MessageList)
async def get_messages(
    chat_id: str,
    before: Optional[str] = Query(None, description="Get messages before this ID"),
    after: Optional[str] = Query(None, description="Get messages after this ID"),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get messages for a chat with cursor-based pagination."""
    # Verify membership
    member_result = await db.execute(
        select(ChatMember).where(
            ChatMember.chat_id == chat_id,
            ChatMember.user_id == current_user.id,
            ChatMember.is_active == True,
        )
    )
    if not member_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this chat",
        )
    
    # Build query
    query = (
        select(Message)
        .options(
            selectinload(Message.sender),
            selectinload(Message.attachments),
            selectinload(Message.reactions),
        )
        .where(
            Message.chat_id == chat_id,
            Message.is_deleted == False,
        )
    )
    
    if before:
        query = query.where(Message.id < before)
    if after:
        query = query.where(Message.id > after)
    
    query = query.order_by(Message.created_at.desc()).limit(limit + 1)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]
    
    # Build responses
    message_responses = []
    for message in reversed(messages):  # Reverse to get chronological order
        response = await get_message_response(message, current_user, db)
        message_responses.append(response)
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Message.id)).where(
            Message.chat_id == chat_id,
            Message.is_deleted == False,
        )
    )
    total = count_result.scalar() or 0
    
    return MessageList(
        messages=message_responses,
        total=total,
        has_more=has_more,
        next_cursor=str(messages[-1].id) if messages and has_more else None,
    )


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis),
):
    """Create a new message."""
    # Verify membership
    member_result = await db.execute(
        select(ChatMember).where(
            ChatMember.chat_id == message_data.chat_id,
            ChatMember.user_id == current_user.id,
            ChatMember.is_active == True,
        )
    )
    member = member_result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this chat",
        )
    
    # Create message
    message = Message(
        chat_id=message_data.chat_id,
        sender_id=current_user.id,
        content=message_data.content,
        message_type=message_data.message_type.value,
        reply_to_id=message_data.reply_to_id,
        forwarded_from_id=message_data.forwarded_from_id,
        status=MessageStatus.SENT.value,
    )
    
    if message_data.metadata:
        import json
        message.extra_data = json.dumps(message_data.metadata)
    
    db.add(message)
    await db.flush()
    
    # Add attachments
    for attachment_data in message_data.attachments:
        attachment = MessageAttachment(
            message_id=message.id,
            file_name=attachment_data.file_name,
            file_url=attachment_data.file_url,
            file_type=attachment_data.file_type,
            file_size=attachment_data.file_size,
            width=attachment_data.width,
            height=attachment_data.height,
            duration=attachment_data.duration,
            thumbnail_url=attachment_data.thumbnail_url,
        )
        db.add(attachment)
    
    # Update chat's last message
    chat_result = await db.execute(
        select(Chat).where(Chat.id == message_data.chat_id)
    )
    chat = chat_result.scalar_one()
    chat.last_message_id = message.id
    chat.last_message_at = message.created_at
    
    # Increment unread count for other members
    members_result = await db.execute(
        select(ChatMember).where(
            ChatMember.chat_id == message_data.chat_id,
            ChatMember.user_id != current_user.id,
            ChatMember.is_active == True,
        )
    )
    for other_member in members_result.scalars():
        other_member.unread_count += 1
        await redis.increment_unread(str(other_member.user_id), str(message_data.chat_id))
    
    await db.commit()
    
    # Reload with relationships
    result = await db.execute(
        select(Message)
        .options(
            selectinload(Message.sender),
            selectinload(Message.attachments),
            selectinload(Message.reactions),
        )
        .where(Message.id == message.id)
    )
    message = result.scalar_one()
    
    return await get_message_response(message, current_user, db)


@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: str,
    message_data: MessageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a message (edit)."""
    result = await db.execute(
        select(Message)
        .options(
            selectinload(Message.sender),
            selectinload(Message.attachments),
            selectinload(Message.reactions),
        )
        .where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    
    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own messages",
        )
    
    if message.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot edit a deleted message",
        )
    
    message.content = message_data.content
    message.is_edited = True
    message.edited_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(message)
    
    return await get_message_response(message, current_user, db)


@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    delete_data: MessageDelete = MessageDelete(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a message."""
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    
    # Check if user can delete
    if message.sender_id != current_user.id:
        # Check if admin
        member_result = await db.execute(
            select(ChatMember).where(
                ChatMember.chat_id == message.chat_id,
                ChatMember.user_id == current_user.id,
                ChatMember.is_active == True,
            )
        )
        member = member_result.scalar_one_or_none()
        if not member or not member.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own messages",
            )
    
    message.is_deleted = True
    message.deleted_at = datetime.utcnow()
    message.deleted_for_everyone = delete_data.delete_for_everyone
    
    if delete_data.delete_for_everyone:
        message.content = None  # Clear content for everyone
    
    await db.commit()
    
    return {"message": "Message deleted successfully"}


@router.post("/{message_id}/reactions", response_model=MessageResponse)
async def add_reaction(
    message_id: str,
    reaction_data: MessageReactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a reaction to a message."""
    result = await db.execute(
        select(Message)
        .options(
            selectinload(Message.sender),
            selectinload(Message.attachments),
            selectinload(Message.reactions),
        )
        .where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    
    # Check membership
    member_result = await db.execute(
        select(ChatMember).where(
            ChatMember.chat_id == message.chat_id,
            ChatMember.user_id == current_user.id,
            ChatMember.is_active == True,
        )
    )
    if not member_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this chat",
        )
    
    # Check for existing reaction with same emoji
    existing_result = await db.execute(
        select(MessageReaction).where(
            MessageReaction.message_id == message_id,
            MessageReaction.user_id == current_user.id,
            MessageReaction.emoji == reaction_data.emoji,
        )
    )
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        # Remove reaction (toggle)
        await db.delete(existing)
    else:
        # Add reaction
        reaction = MessageReaction(
            message_id=message.id,
            user_id=current_user.id,
            emoji=reaction_data.emoji,
        )
        db.add(reaction)
    
    await db.commit()
    
    # Reload message
    result = await db.execute(
        select(Message)
        .options(
            selectinload(Message.sender),
            selectinload(Message.attachments),
            selectinload(Message.reactions),
        )
        .where(Message.id == message_id)
    )
    message = result.scalar_one()
    
    return await get_message_response(message, current_user, db)


@router.post("/{message_id}/pin")
async def pin_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pin/unpin a message."""
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    
    # Check if admin
    member_result = await db.execute(
        select(ChatMember).where(
            ChatMember.chat_id == message.chat_id,
            ChatMember.user_id == current_user.id,
            ChatMember.is_active == True,
        )
    )
    member = member_result.scalar_one_or_none()
    
    if not member or not member.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can pin messages",
        )
    
    message.is_pinned = not message.is_pinned
    message.pinned_at = datetime.utcnow() if message.is_pinned else None
    
    await db.commit()
    
    return {"is_pinned": message.is_pinned}


@router.get("/chat/{chat_id}/pinned", response_model=List[MessageResponse])
async def get_pinned_messages(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all pinned messages in a chat."""
    # Check membership
    member_result = await db.execute(
        select(ChatMember).where(
            ChatMember.chat_id == chat_id,
            ChatMember.user_id == current_user.id,
            ChatMember.is_active == True,
        )
    )
    if not member_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this chat",
        )
    
    result = await db.execute(
        select(Message)
        .options(
            selectinload(Message.sender),
            selectinload(Message.attachments),
            selectinload(Message.reactions),
        )
        .where(
            Message.chat_id == chat_id,
            Message.is_pinned == True,
            Message.is_deleted == False,
        )
        .order_by(Message.pinned_at.desc())
    )
    messages = result.scalars().all()
    
    return [await get_message_response(m, current_user, db) for m in messages]


@router.post("/chat/{chat_id}/read")
async def mark_as_read(
    chat_id: str,
    message_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis),
):
    """Mark messages as read in a chat."""
    member_result = await db.execute(
        select(ChatMember).where(
            ChatMember.chat_id == chat_id,
            ChatMember.user_id == current_user.id,
            ChatMember.is_active == True,
        )
    )
    member = member_result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this chat",
        )
    
    # Update member's read status
    if message_id:
        member.last_read_message_id = message_id
    member.last_read_at = datetime.utcnow()
    member.unread_count = 0
    
    # Clear unread in Redis
    await redis.clear_unread(str(current_user.id), chat_id)
    
    await db.commit()
    
    return {"message": "Marked as read"}

