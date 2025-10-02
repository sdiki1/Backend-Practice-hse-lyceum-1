# type: ignore
from typing import Optional

from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import schemas
from pydantic import BaseModel

from backend.db.models.users import UserPrivacy, UserStatus


class OAuth2PasswordRequestFormWithEmail(OAuth2PasswordRequestForm):
    """My hack to authenticate user using email instead of username."""

    email: str
    password: str

    def __init__(
        self,
        email: str = Form(..., description="User email address"),
        password: str = Form(..., description="User password"),
    ) -> None:
        super().__init__(username=email, password=password)


class UserCreate(schemas.BaseUserCreate):
    """Create user schema."""

    secret_word: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: str = "UTC"
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    privacy_level: UserPrivacy = UserPrivacy.PUBLIC
    preferred_language: str = "ru"
    status: Optional[UserStatus] = UserStatus.ACTIVE


class ChangePasswordRequest(BaseModel):
    """Change password schema."""

    current_password: str = Form(..., description="Current password")
    new_password: str = Form(..., description="New password")
    secret_word: Optional[str] = Form(None, description="Secret word if set")
