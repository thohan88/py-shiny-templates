from starlette.middleware import Middleware
from starlette.responses import RedirectResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.types import ASGIApp, Receive, Scope, Send
from .config import settings
import os
import jwt


class AuthMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] in ["http", "websocket"]:
            allowed_paths = ["/api", "/login"]
            allowed_paths = [os.path.normpath(settings.path_root + path) for path in allowed_paths]
            requested_path = (settings.path_proxy or "") + scope["path"]

            # Check if the requested path is allowed without authentication
            if not any(requested_path.startswith(path) for path in allowed_paths):
                # If the path is not allowed, check for authentication
                cookies = dict(scope["headers"]).get(b"cookie", b"").decode("utf-8")
                jwt_token = next(
                    (
                        cookie.split("=")[1]
                        for cookie in cookies.split("; ")
                        if "fastapiusersauth" in cookie
                    ),
                    None,
                )

                try:
                    user = jwt.decode(
                        jwt_token,
                        settings.jwt_secret,
                        audience=["fastapi-users:auth"],
                        algorithms=["HS256"],
                    )
                except (jwt.exceptions.DecodeError, TypeError):
                    return await self.handle_unauthenticated(scope, receive, send)

                if not user:
                    return await self.handle_unauthenticated(scope, receive, send)

        # Allow request to continue for allowed paths or authenticated requests
        return await self.app(scope, receive, send)

    async def handle_unauthenticated(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            redirect_path = settings.path_root + "/login/"
            return await RedirectResponse(redirect_path)(scope, receive, send)
        elif scope["type"] == "websocket":
            websocket = WebSocket(scope, receive, send)
            await websocket.close(code=1008)
            raise WebSocketDisconnect(code=1008)


auth_middleware = [Middleware(AuthMiddleware)]
