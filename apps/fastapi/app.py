from starlette.applications import Starlette
from .fastapi import app as fastapi_app
from .shiny import app as shiny_app

app = Starlette()
app.mount("/api", fastapi_app)
app.mount("/", shiny_app)

