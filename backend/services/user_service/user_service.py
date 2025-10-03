# type: ignore
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.dao.users_dao import UserDAO
from backend.db.dependencies import get_db_session
from backend.db.models.users import User, UserManager, get_user_manager


class UserService:
    """Service for user-related operations."""

    def __init__(self, session: AsyncSession, user_manager: UserManager) -> None:
        self.user_dao = UserDAO(session)
        self.user_manager = user_manager

    async def verify_password(self, user: User, password: str) -> bool:
        """Verify if the provided password matches the user's current password."""

        (
            verified,
            updated_password_hash,
        ) = self.user_manager.password_helper.verify_and_update(
            password,
            user.hashed_password,
        )

        if verified and updated_password_hash is not None:
            await self.user_dao.update_password(
                user.id,
                updated_password_hash,
                update_last_password_change=False,
            )

        return verified

    async def validate_new_password(self, user: User, new_password: str) -> None:
        """Validate that the new password."""
        if await self.verify_password(user, new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from your current password",
            )
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters or long",
            )

    async def validate_secret_word(
        self,
        user: User,
        secret_word: Optional[str] = None,
    ) -> None:
        """Validate secret word if the user has it else skip."""

        if user.secret_word:
            if not secret_word:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Secret word is required for this account",
                )

            if user.secret_word != secret_word:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Secret word is incorrect",
                )

    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
        secret_word: Optional[str] = None,
    ) -> None:
        """Change user password function.

        :param user_id: User ID.
        :param current_password: Current not cashed password.
        :param new_password: New not cashed password.
        :param secret_word: Secret word if it exists.
        :return: None or raise http exception, if sth went wrong.
        """

        user = await self.user_dao.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not await self.verify_password(user, current_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        await self.validate_secret_word(user, secret_word)

        await self.validate_new_password(user, new_password)

        hashed_password = self.user_manager.password_helper.hash(new_password)

        success = await self.user_dao.update_password(
            user_id,
            hashed_password,
            update_last_password_change=True,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password",
            )

    async def get_user_profile(self, user_id: UUID) -> Optional[User]:
        """Get user profile by their id."""
        return await self.user_dao.get_user_by_id(user_id)

    async def update_user_profile(self, user_id: UUID, update_data: dict) -> bool:
        """Update user's progile information."""
        user = await self.get_user_profile(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        success = await self.user_dao.update_user_profile(user_id, update_data)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile",
            )

        return True

    async def record_user_activity(self, user_id: UUID) -> bool:
        """Record user activity timestamp."""

        return await self.user_dao.update_last_activity(user_id)

    async def get_client_ip(self, request: Request) -> str:
        """Get client IP address."""

        if "x-forwarded-for" in request.headers:
            ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        elif "x-real-ip" in request.headers:
            ip = request.headers["x-real-ip"]
        else:
            ip = request.client.host

        return ip

    async def update_user_last_login(
        self,
        user_id: UUID,
        request: Optional[Request] = None,
    ) -> bool:
        """Update user's last login timestamp and IP."""

        update_data = {
            "last_login_at": datetime.now(timezone.utc),
            "last_activity_at": datetime.now(timezone.utc),
        }
        ip_address = await self.get_client_ip(request)

        update_data["last_login_ip"] = ip_address
        update_data["last_using_ip"] = ip_address

        return await self.user_dao.update_user_profile(user_id, update_data)

    async def update_user_registration(
        self,
        user_id: UUID,
        request: Optional[Request] = None,
    ) -> bool:
        """Update user's registration timestamp and IP."""

        update_data = {
            "last_activity_at": datetime.now(timezone.utc),
        }
        if request:
            ip_address = await self.get_client_ip(request)
            update_data["last_using_ip"] = ip_address
            update_data["registration_ip"] = ip_address

        return await self.user_dao.update_user_profile(user_id, update_data)


def get_user_service(
    session: AsyncSession = Depends(get_db_session),
    user_manager: UserManager = Depends(get_user_manager),
) -> UserService:
    """Dependency for UserService, return UserService instance."""
    return UserService(session, user_manager)
