"""
ChatFlow - Chats Router
"""

import secrets
from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.redis import RedisManager, get_redis
from app.models.chat import Chat, ChatMember, ChatType, MemberRole
from app.models.message import Message
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.chat import (
    ChatCreate,
    ChatInviteLink,
    ChatListResponse,
    ChatMemberAdd,
    ChatMemberResponse,
    ChatMemberUpdate,
    ChatResponse,
    ChatUpdate,
    LastMessagePreview,
)
from app.schemas.user import UserProfile

router = APIRouter()


@router.get("/", response_model=List[ChatListResponse])
async def get_chats(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis),
):
    """Get all chats for current user."""
    # Get chat memberships
    result = await db.execute(
        select(ChatMember)
        .options(selectinload(ChatMember.chat))
        .where(
            ChatMember.user_id == current_user.id,
            ChatMember.is_active == True,
        )
        .order_by(ChatMember.is_pinned.desc())
    )
    memberships = result.scalars().all()
    
    chat_responses = []
    for membership in memberships:
        chat = membership.chat
        if not chat.is_active:
            continue
        
        # Build response
        chat_response = ChatListResponse(
            id=chat.id,
            name=chat.name,
            avatar_url=chat.avatar_url,
            chat_type=chat.chat_type,
            is_muted=membership.is_muted,
            is_pinned=membership.is_pinned,
            unread_count=membership.unread_count,
            last_message_at=chat.last_message_at,
        )
        
        # For private chats, get other user info
        if chat.chat_type == ChatType.PRIVATE.value:
            other_member_result = await db.execute(
                select(ChatMember)
                .options(selectinload(ChatMember.user))
                .where(
                    ChatMember.chat_id == chat.id,
                    ChatMember.user_id != current_user.id,
                )
            )
            other_member = other_member_result.scalar_one_or_none()
            if other_member and other_member.user:
                chat_response.other_user = UserProfile.model_validate(other_member.user)
                chat_response.name = other_member.user.full_name
                chat_response.avatar_url = other_member.user.avatar_url
                chat_response.is_online = await redis.is_user_online(str(other_member.user.id))
        
        # Get last message
        if chat.last_message_id:
            msg_result = await db.execute(
                select(Message)
                .options(selectinload(Message.sender))
                .where(Message.id == chat.last_message_id)
            )
            last_message = msg_result.scalar_one_or_none()
            if last_message:
                chat_response.last_message = LastMessagePreview(
                    id=last_message.id,
                    content=last_message.content[:100] if last_message.content else None,
                    message_type=last_message.message_type,
                    sender_id=last_message.sender_id,
                    sender_name=last_message.sender.full_name if last_message.sender else None,
                    created_at=last_message.created_at,
                )
        
        chat_responses.append(chat_response)
    
    # Sort by last message time
    chat_responses.sort(
        key=lambda x: (not x.is_pinned, x.last_message_at or x.id),
        reverse=True,
    )
    
    return chat_responses[offset:offset + limit]


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat."""
    # Validate members exist
    if chat_data.member_ids:
        result = await db.execute(
            select(User).where(
                User.id.in_(chat_data.member_ids),
                User.is_active == True,
            )
        )
        valid_users = result.scalars().all()
        valid_user_ids = {user.id for user in valid_users}
        invalid_ids = set(chat_data.member_ids) - valid_user_ids
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Users not found: {invalid_ids}",
            )
    
    # For private chat, check if one already exists
    if chat_data.chat_type == ChatType.PRIVATE:
        if len(chat_data.member_ids) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Private chat must have exactly one other member",
            )
        
        other_user_id = chat_data.member_ids[0]
        
        # Check for existing private chat
        existing_chat = await db.execute(
            select(Chat)
            .join(ChatMember)
            .where(
                Chat.chat_type == ChatType.PRIVATE.value,
                ChatMember.user_id == current_user.id,
            )
        )
        for chat in existing_chat.scalars():
            members_result = await db.execute(
                select(ChatMember.user_id).where(ChatMember.chat_id == chat.id)
            )
            member_ids = {row[0] for row in members_result.fetchall()}
            if member_ids == {current_user.id, other_user_id}:
                # Return existing chat
                return await get_chat(str(chat.id), current_user, db)
    
    # Create chat
    chat = Chat(
        name=chat_data.name,
        description=chat_data.description,
        avatar_url=chat_data.avatar_url,
        chat_type=chat_data.chat_type.value,
    )
    
    # Generate invite link for groups
    if chat_data.chat_type in [ChatType.GROUP, ChatType.CHANNEL]:
        chat.invite_link = secrets.token_urlsafe(16)
    
    db.add(chat)
    await db.flush()
    
    # Add current user as owner
    owner_member = ChatMember(
        chat_id=chat.id,
        user_id=current_user.id,
        role=MemberRole.OWNER.value,
    )
    db.add(owner_member)
    
    # Add other members
    for user_id in chat_data.member_ids:
        member = ChatMember(
            chat_id=chat.id,
            user_id=user_id,
            role=MemberRole.MEMBER.value,
        )
        db.add(member)
    
    await db.commit()
    await db.refresh(chat)
    
    return await get_chat(str(chat.id), current_user, db)


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get chat by ID."""
    result = await db.execute(
        select(Chat)
        .options(selectinload(Chat.members).selectinload(ChatMember.user))
        .where(Chat.id == chat_id)
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )
    
    # Check if user is a member
    is_member = any(m.user_id == current_user.id and m.is_active for m in chat.members)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this chat",
        )
    
    # Build response
    members = [
        ChatMemberResponse(
            id=m.id,
            user_id=m.user_id,
            role=m.role,
            nickname=m.nickname,
            is_active=m.is_active,
            joined_at=m.joined_at,
            user=UserProfile.model_validate(m.user) if m.user else None,
        )
        for m in chat.members
        if m.is_active
    ]
    
    return ChatResponse(
        id=chat.id,
        name=chat.name,
        description=chat.description,
        avatar_url=chat.avatar_url,
        chat_type=chat.chat_type,
        is_active=chat.is_active,
        invite_link=chat.invite_link,
        last_message_at=chat.last_message_at,
        created_at=chat.created_at,
        members=members,
        member_count=len(members),
    )


@router.put("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: str,
    chat_data: ChatUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update chat settings (admin only)."""
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id)
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )
    
    # Check if user is admin
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
    
    if not member.is_admin and chat.chat_type != ChatType.PRIVATE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update chat settings",
        )
    
    # Update fields
    update_data = chat_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chat, field, value)
    
    await db.commit()
    
    return await get_chat(chat_id, current_user, db)


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a chat (owner only)."""
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id)
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )
    
    # Check if user is owner
    member_result = await db.execute(
        select(ChatMember).where(
            ChatMember.chat_id == chat_id,
            ChatMember.user_id == current_user.id,
            ChatMember.role == MemberRole.OWNER.value,
        )
    )
    
    if not member_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can delete this chat",
        )
    
    # Soft delete
    chat.is_active = False
    await db.commit()
    
    return {"message": "Chat deleted successfully"}


@router.post("/{chat_id}/members", response_model=List[ChatMemberResponse])
async def add_members(
    chat_id: str,
    member_data: ChatMemberAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add members to a chat (admin only)."""
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id)
    )
    chat = result.scalar_one_or_none()
    
    if not chat or not chat.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )
    
    if chat.chat_type == ChatType.PRIVATE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add members to private chat",
        )
    
    # Check if user is admin
    member_result = await db.execute(
        select(ChatMember).where(
            ChatMember.chat_id == chat_id,
            ChatMember.user_id == current_user.id,
            ChatMember.is_active == True,
        )
    )
    current_member = member_result.scalar_one_or_none()
    
    if not current_member or not current_member.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can add members",
        )
    
    # Add new members
    new_members = []
    for user_id in member_data.user_ids:
        # Check if already a member
        existing = await db.execute(
            select(ChatMember).where(
                ChatMember.chat_id == chat_id,
                ChatMember.user_id == user_id,
            )
        )
        existing_member = existing.scalar_one_or_none()
        
        if existing_member:
            if not existing_member.is_active:
                existing_member.is_active = True
                existing_member.role = member_data.role.value
                new_members.append(existing_member)
        else:
            member = ChatMember(
                chat_id=chat.id,
                user_id=user_id,
                role=member_data.role.value,
            )
            db.add(member)
            new_members.append(member)
    
    await db.commit()
    
    # Refresh and return
    result = []
    for member in new_members:
        await db.refresh(member)
        user_result = await db.execute(select(User).where(User.id == member.user_id))
        user = user_result.scalar_one_or_none()
        result.append(ChatMemberResponse(
            id=member.id,
            user_id=member.user_id,
            role=member.role,
            nickname=member.nickname,
            is_active=member.is_active,
            joined_at=member.joined_at,
            user=UserProfile.model_validate(user) if user else None,
        ))
    
    return result


@router.delete("/{chat_id}/members/{user_id}")
async def remove_member(
    chat_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a member from chat."""
    # Check if current user is admin or removing themselves
    is_self = str(current_user.id) == user_id
    
    member_result = await db.execute(
        select(ChatMember).where(
            ChatMember.chat_id == chat_id,
            ChatMember.user_id == current_user.id,
            ChatMember.is_active == True,
        )
    )
    current_member = member_result.scalar_one_or_none()
    
    if not current_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this chat",
        )
    
    if not is_self and not current_member.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can remove members",
        )
    
    # Get target member
    target_result = await db.execute(
        select(ChatMember).where(
            ChatMember.chat_id == chat_id,
            ChatMember.user_id == user_id,
            ChatMember.is_active == True,
        )
    )
    target_member = target_result.scalar_one_or_none()
    
    if not target_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )
    
    # Cannot remove owner
    if target_member.role == MemberRole.OWNER.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the owner",
        )
    
    target_member.is_active = False
    await db.commit()
    
    return {"message": "Member removed successfully"}


@router.post("/{chat_id}/invite-link", response_model=ChatInviteLink)
async def generate_invite_link(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new invite link (admin only)."""
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id)
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )
    
    # Check admin permission
    member_result = await db.execute(
        select(ChatMember).where(
            ChatMember.chat_id == chat_id,
            ChatMember.user_id == current_user.id,
            ChatMember.is_active == True,
        )
    )
    member = member_result.scalar_one_or_none()
    
    if not member or not member.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can generate invite links",
        )
    
    chat.invite_link = secrets.token_urlsafe(16)
    await db.commit()
    
    return ChatInviteLink(
        chat_id=chat.id,
        invite_link=chat.invite_link,
    )


@router.post("/join/{invite_link}", response_model=ChatResponse)
async def join_chat(
    invite_link: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Join a chat using invite link."""
    result = await db.execute(
        select(Chat).where(
            Chat.invite_link == invite_link,
            Chat.is_active == True,
        )
    )
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite link",
        )
    
    # Check if already a member
    member_result = await db.execute(
        select(ChatMember).where(
            ChatMember.chat_id == chat.id,
            ChatMember.user_id == current_user.id,
        )
    )
    existing = member_result.scalar_one_or_none()
    
    if existing:
        if existing.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already a member of this chat",
            )
        existing.is_active = True
    else:
        member = ChatMember(
            chat_id=chat.id,
            user_id=current_user.id,
            role=MemberRole.MEMBER.value,
        )
        db.add(member)
    
    await db.commit()
    
    return await get_chat(str(chat.id), current_user, db)

