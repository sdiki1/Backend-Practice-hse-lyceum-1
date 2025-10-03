# type: ignore
from typing import List, Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.dependencies import get_db_session
from backend.db.models.posts import Post


class PostDAO:
    """Data Access Object for User operations."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def create_post_model(self, title: str, content: str, user_id: UUID) -> Post:
        """
        Add single post to session and return created post.

        :param title: title of post.
        :param content: content of post.
        :param user_id: id user, who created the post.
        :return: Created Post object.
        """
        post = Post(user_id=user_id, title=title, content=content)
        self.session.add(post)

        await self.session.flush()
        await self.session.refresh(post)

        return post

    async def get_all_posts(self, limit: int, offset: int) -> List[Post]:
        """
        Get all posts models with limit/offset pagination.

        Later i'll be normally recommendation system,
        but for now only how database it returns.

        :param limit: limit of posts.
        :param offset: offset of posts.
        :return: stream of posts.
        """

        raw_posts = await self.session.execute(
            select(Post).limit(limit).offset(offset),
        )

        return list(raw_posts.scalars().fetchall())

    async def filter_by_title(self, title: Optional[str] = None) -> List[Post]:
        """
        Get specific post model.

        :param title: title of post instance.
        :return: post models.
        """

        query = select(Post)
        if title:
            query = query.where(Post.title == title)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())

    async def update_post(
        self,
        user_id: UUID,
        post_id: int,
        title: str = "",
        content: str = "",
    ) -> Optional[Post | bool]:
        """
        Update post model.

        :param user_id: id user, who created the post.
        :param post_id: id of post.
        :param title: title of post, if None -> will not be changed.
        :param content: content of post, if None -> will not be changed.
        :return bool: if True post was updated, else False.
        """
        post_raw = await self.session.execute(select(Post).where(Post.id == post_id))
        post = post_raw.scalars().fetchall()[0]
        if post.user_id != user_id:
            return False

        if title:
            await self.session.execute(
                update(Post).where(Post.id == post_id).values(title=title),
            )
        if content:
            await self.session.execute(
                update(Post).where(Post.id == post_id).values(content=content),
            )
        post_raw = await self.session.execute(select(Post).where(Post.id == post_id))
        return post_raw.scalars().fetchall()[0]

    async def get_post_by_id(self, post_id: int) -> Optional[Post | None]:
        """Get post by id."""

        post_raw = await self.session.execute(select(Post).where(Post.id == post_id))
        return post_raw.scalars().fetchall()[0]

    async def delete_post(self, post_id: int, user_id: UUID) -> Optional[bool]:
        """Delete post by id."""

        post_raw = await self.session.execute(select(Post).where(Post.id == post_id))
        try:
            post = post_raw.scalars().fetchall()[0]
        except Exception as _:
            return False
        if post.user_id != user_id:
            return False
        await self.session.execute(delete(Post).where(Post.id == post.id))
        return True
