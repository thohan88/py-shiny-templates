from fastapi import Response, status
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users import models
from ...config import settings


class RedirectCookieAuthentication(CookieTransport):
    async def get_login_response(self, token: str) -> Response:
        response = Response(status_code=status.HTTP_302_FOUND)
        response.headers["Location"] = settings.path_root + "/"
        return self._set_login_cookie(response, token)

    async def get_logout_response(self) -> Response:
        response = Response(status_code=status.HTTP_302_FOUND)
        response.headers["Location"] = settings.path_root + "/"
        return self._set_logout_cookie(response)


cookie_transport = RedirectCookieAuthentication(cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=settings.jwt_secret, lifetime_seconds=3600)


web_backend = AuthenticationBackend(
    name="web",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
