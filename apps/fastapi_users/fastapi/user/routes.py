from fastapi import APIRouter
from .schemas import UserRead, UserUpdate
from ..auth.services import fastapi_users

user_router = APIRouter()

user_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)
