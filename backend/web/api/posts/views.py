# type: ignore
from fastapi import APIRouter, Response, status
from fastapi.param_functions import Depends

from backend.db.dao.posts_dao import PostDAO
from backend.db.models.users import User, current_active_user
from backend.schemas.post import PostModelDTO, PostModelInputDTO, PostModelUpdateDTO

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_post_model(
    new_post_object: PostModelInputDTO,
    user: User = Depends(current_active_user),
    post_dao: PostDAO = Depends(),
) -> PostModelDTO:
    """
    Creates post model in the database.

    :param new_post_object: new post model item.
    :param post_dao: DAO for post models.
    """
    return await post_dao.create_post_model(
        title=new_post_object.title,
        content=new_post_object.content,
        user_id=user.id,
    )


@router.patch("/{post_id}")
async def update_post_model(
    edit_post_object: PostModelUpdateDTO,
    user: User = Depends(current_active_user),
    post_dao: PostDAO = Depends(),
    post_id: int = 0,
) -> PostModelDTO:
    """
    Update post model in the database.

    :param edit_post_object: post model field to update.
    :param user: authenticated user.
    :param post_dao: DAO for post models.
    :param post_id: id of post to update.
    """
    result = await post_dao.update_post(
        user_id=user.id,
        post_id=post_id,
        title=edit_post_object.title,
        content=edit_post_object.content,
    )
    if result:
        return result
    return Response(
        '{"Error": "Post not found"}',
        status.HTTP_404_NOT_FOUND,
        media_type="application/json",
    )


@router.get("/{post_id}")
async def get_post_model(
    post_id: int = 0,
    post_dao: PostDAO = Depends(),
) -> PostModelDTO:
    """Get post model from the database.

    :param post_id: id of post to get.
    """
    return await post_dao.get_post_by_id(post_id=post_id)


@router.delete("/{post_id}")
async def delete_post_model(
    post_id: int = 0,
    user: User = Depends(current_active_user),
    post_dao: PostDAO = Depends(),
) -> Response:
    """Delete post instanse."""

    result = await post_dao.delete_post(post_id, user.id)
    if result:
        return Response(
            '{"status": "deleted"}',
            status.HTTP_200_OK,
            media_type="application/json",
        )
    return Response(
        '{"status": "error"}',
        status.HTTP_400_BAD_REQUEST,
        media_type="application/json",
    )
