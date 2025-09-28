# type: ignore
import uuid
from datetime import datetime
from typing import Optional

from fastapi_users import schemas
from pydantic import EmailStr

from backend.db.models.users import UserPrivacy, UserStatus


class UserBase(schemas.BaseUser[uuid.UUID]):
    """Base user schema."""

    email: EmailStr
    phone_number: Optional[str] = None
    timezone: str = "UTC"
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    privacy_level: UserPrivacy = UserPrivacy.PUBLIC
    preferred_language: str = "ru"


class UserUpdate(UserBase):
    """Update user schema."""

    password: Optional[str] = None
    secret_word: Optional[str] = None


class UserResponse(UserBase):
    """User response schema."""

    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    last_activity_at: Optional[datetime]
    status: UserStatus

    class Config:
        from_attributes = True
