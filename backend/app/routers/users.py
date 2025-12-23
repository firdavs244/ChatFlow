"""
ChatFlow - Users Router
"""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import RedisManager, get_redis
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.user import (
    PasswordChange,
    UserProfile,
    UserResponse,
    UserSearch,
    UserUpdate,
)

router = APIRouter()


@router.get("/search", response_model=List[UserProfile])
async def search_users(
    query: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search users by username or full name."""
    search_query = f"%{query}%"
    
    result = await db.execute(
        select(User)
        .where(
            User.is_active == True,
            User.id != current_user.id,
            or_(
                User.username.ilike(search_query),
                User.full_name.ilike(search_query),
            ),
        )
        .limit(limit)
        .offset(offset)
    )
    
    users = result.scalars().all()
    return [UserProfile.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserProfile)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis),
):
    """Get user profile by ID."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    profile = UserProfile.model_validate(user)
    
    # Check online status
    if await redis.is_user_online(str(user.id)):
        profile.status = "online"
    
    return profile


@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile."""
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.post("/me/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change current user password."""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/me/avatar")
async def update_avatar(
    avatar_url: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user avatar URL."""
    current_user.avatar_url = avatar_url
    await db.commit()
    
    return {"avatar_url": avatar_url}


@router.get("/me/online-contacts", response_model=List[UserProfile])
async def get_online_contacts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis),
):
    """Get online users from current user's contacts (chat partners)."""
    from app.models.chat import ChatMember, Chat, ChatType
    
    # Get all private chats for current user
    result = await db.execute(
        select(ChatMember.chat_id)
        .join(Chat)
        .where(
            ChatMember.user_id == current_user.id,
            ChatMember.is_active == True,
            Chat.chat_type == ChatType.PRIVATE.value,
        )
    )
    chat_ids = [row[0] for row in result.fetchall()]
    
    if not chat_ids:
        return []
    
    # Get other users in these chats
    result = await db.execute(
        select(User)
        .join(ChatMember)
        .where(
            ChatMember.chat_id.in_(chat_ids),
            ChatMember.user_id != current_user.id,
            ChatMember.is_active == True,
            User.is_active == True,
        )
    )
    users = result.scalars().all()
    
    # Filter online users
    online_users = []
    for user in users:
        if await redis.is_user_online(str(user.id)):
            profile = UserProfile.model_validate(user)
            profile.status = "online"
            online_users.append(profile)
    
    return online_users

