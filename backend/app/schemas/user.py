"""
ChatFlow - User Schemas
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema."""
    
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").replace(".", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores and dots allowed)")
        return v.lower()
    
    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = None
    status_message: Optional[str] = Field(None, max_length=200)


class UserResponse(BaseModel):
    """Schema for user response."""
    
    id: UUID
    email: EmailStr
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    status: str
    last_seen: Optional[datetime] = None
    status_message: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """Public user profile (for other users)."""
    
    id: UUID
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    status: str
    last_seen: Optional[datetime] = None
    status_message: Optional[str] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Schema for refreshing access token."""
    
    refresh_token: str


class PasswordChange(BaseModel):
    """Schema for changing password."""
    
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserSearch(BaseModel):
    """Schema for searching users."""
    
    query: str = Field(..., min_length=1, max_length=100)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

