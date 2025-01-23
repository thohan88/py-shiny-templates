from fastapi import APIRouter, Depends, HTTPException, status
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.google import GoogleOAuth2
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.manager import BaseUserManager
from .models import User
from .services import get_user_manager, web_backend
from .services import fastapi_users
from ..user.schemas import UserCreate, UserRead
from ...config import settings
import uuid

auth_router = APIRouter()

google_oauth_client = GoogleOAuth2(
    client_id = settings.google_client_id,
    client_secret = settings.google_client_secret,
)

auth_router.include_router(
    fastapi_users.get_auth_router(web_backend), prefix="/web", tags=["auth"]
)

auth_router.include_router(
    fastapi_users.get_oauth_router(
        oauth_client = google_oauth_client,
        backend = web_backend,
        state_secret=settings.jwt_secret,
        associate_by_email=True,
        is_verified_by_default=True,
        redirect_url=settings.google_redirect_uri
    ),
    prefix="/google",
    
    tags=["auth"],
)

auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    tags=["auth"],
)
auth_router.include_router(
    fastapi_users.get_reset_password_router(),
    tags=["auth"],
)
auth_router.include_router(
    fastapi_users.get_verify_router(UserRead),
    tags=["auth"],
)


@auth_router.post("/validate-credentials", tags=["auth"])
async def validate_credentials(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_manager: BaseUserManager[User, uuid.UUID] = Depends(get_user_manager),
):
    user = await user_manager.authenticate(form_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    return {"message": "Credentials are valid"}
