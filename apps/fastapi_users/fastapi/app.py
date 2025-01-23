from fastapi import FastAPI
from .auth.routes import auth_router
from .user.routes import user_router
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI()

app = FastAPI(docs_url=None, servers=[{'url': './'}], root_path_in_servers=False)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="openapi.json",
        title="Docs"
    )

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/user", tags=["user"])
