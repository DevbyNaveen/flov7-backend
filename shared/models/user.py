"""
User data models for Flov7 platform.
Pydantic models for user-related data structures.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    role: str = "user"
    subscription_plan: str = "free"


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update model"""
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    subscription_plan: Optional[str] = None


class UserInDB(UserBase):
    """User model as stored in database"""
    id: UUID
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    subscription_expires_at: Optional[datetime] = None


class UserResponse(UserBase):
    """User response model"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    subscription_expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """User profile information"""
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    subscription_plan: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class Token(BaseModel):
    """JWT token model"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Token data model"""
    email: Optional[str] = None
    user_id: Optional[str] = None
