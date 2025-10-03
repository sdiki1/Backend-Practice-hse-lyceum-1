# type: ignore
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from backend.db.models.users import (
    User,
    UserManager,
    api_users,
    auth_jwt,
    current_active_user,
    get_user_manager,
)
from backend.schemas.auth import (
    ChangePasswordRequest,
    OAuth2PasswordRequestFormWithEmail,
    UserCreate,
)
from backend.schemas.users import UserResponse
from backend.services.user_service import UserService, get_user_service

router = APIRouter()

router.include_router(
    api_users.get_register_router(UserResponse, UserCreate),
    tags=["auth"],
)


@router.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestFormWithEmail = Depends(),
    user_manager: UserManager = Depends(get_user_manager),
    user_service: UserService = Depends(get_user_service),
) -> Response:
    """Login user by email and password. Return JWT access token."""
    user = await user_manager.authenticate(form_data)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    response = await auth_jwt.login(auth_jwt.get_strategy(), user)
    await user_service.update_user_last_login(user.id, request)
    await user_manager.on_after_login(user)
    return response


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    user: User = Depends(current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    """Change password for current user."""

    await user_service.change_password(
        user_id=user.id,
        current_password=request.current_password,
        new_password=request.new_password,
        secret_word=request.secret_word,
    )

    return {"message": "Password updated successfully", "password_changed": True}
