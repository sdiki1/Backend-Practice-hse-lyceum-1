# type: ignore
from fastapi.routing import APIRouter

from backend.web.api import auth, docs, dummy, echo, monitoring, posts, redis, users

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router)
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(docs.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
