from fastapi import APIRouter

from router.user import router as user_router

v1router = APIRouter()

v1router.include_router(
    prefix='/user',
    router=user_router
)