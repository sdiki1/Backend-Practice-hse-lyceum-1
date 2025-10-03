# type: ignore
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.db.models.users import User


class UserDAO:
    """Data Access Object for User operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def update_password(
        self,
        user_id: UUID,
        hashed_password: str,
        update_last_password_change: bool = True,
    ) -> bool:
        """Update user password."""
        try:
            update_values = {"hashed_password": hashed_password}

            if update_last_password_change:
                update_values["last_password_change"] = datetime.now(timezone.utc)

            stmt = sql_update(User).where(User.id == user_id).values(**update_values)

            result = await self.session.execute(stmt)
            await self.session.commit()

            return result.rowcount > 0

        except Exception:
            await self.session.rollback()
            return False

    async def update_user_profile(self, user_id: UUID, update_data: dict) -> bool:
        """Update user profile data."""
        try:
            if not update_data:
                return False

            # Ensure we don't update sensitive fields directly
            restricted_fields = {
                "hashed_password",
                "id",
                "is_superuser",
                "created_at",
                "secret_word",
                "updated_at",
                "last_password_change",
            }

            filtered_data = {
                k: v for k, v in update_data.items() if k not in restricted_fields
            }

            if not filtered_data:
                return False

            stmt = sql_update(User).where(User.id == user_id).values(**filtered_data)

            result = await self.session.execute(stmt)
            await self.session.commit()

            return result.rowcount > 0

        except Exception:
            await self.session.rollback()
            return False

    async def update_last_activity(self, user_id: UUID) -> bool:
        """Update user's last activity timestamp."""
        try:
            stmt = (
                sql_update(User)
                .where(User.id == user_id)
                .values(last_activity_at=datetime.now(timezone.utc))
            )

            result = await self.session.execute(stmt)
            await self.session.commit()

            return result.rowcount > 0

        except Exception:
            await self.session.rollback()
            return False
