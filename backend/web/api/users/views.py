# type: ignore
from fastapi import APIRouter

from backend.db.models.users import api_users
from backend.schemas.users import UserResponse, UserUpdate

router = APIRouter()

router.include_router(
    api_users.get_users_router(UserResponse, UserUpdate),
    prefix="/users",
    tags=["users"],
)
