from fastapi import APIRouter

from backend.db.models.users import (
    api_users,  # type: ignore
    auth_jwt,  # type: ignore
)
from backend.schemas.users import (
    UserCreate,
    UserResponse,
    UserUpdate,
)

router = APIRouter()

router.include_router(
    api_users.get_register_router(UserResponse, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    api_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    api_users.get_verify_router(UserResponse),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    api_users.get_users_router(UserResponse, UserUpdate),
    prefix="/users",
    tags=["users"],
)
router.include_router(
    api_users.get_auth_router(auth_jwt),
    prefix="/auth/jwt",
    tags=["auth"],
)
