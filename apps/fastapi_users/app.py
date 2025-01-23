from starlette.applications import Starlette
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .fastapi.app import app as fastapi_app
from .fastapi.core.database import create_db_and_tables, destroy_db
from .shiny.app import app as shiny_app
from .shiny.app_register_login import app as app_register_login
from .auth import auth_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield
    await destroy_db()


# Define a run_app which can be used to test modules
# while still mounting backend and registration/login.
# In a module, you can then use `run_app(module_app)`.
def run_app(
    shiny_app,
    fastapi_app=fastapi_app,
    app_register_login=app_register_login,
    lifespan=lifespan,
    auth_middleware=auth_middleware,
):
    app = Starlette(lifespan=lifespan, middleware=auth_middleware)
    app.mount("/api", fastapi_app)
    app.mount("/login", app_register_login)
    app.mount("/", shiny_app)
    return app


app = run_app(shiny_app)
