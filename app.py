from starlette.applications import Starlette
from apps.dark_theme.app import app as app_dark_theme
from apps.fastapi.app import app as app_fastapi
from apps.fastapi_users.app import app as app_fastapi_users
from apps.input_search.app import app as app_input_search
from apps.leaflet_live_positions.app import app as app_leaflet_live_positions
from apps.leaflet_retina_tiles.app import app as app_leaflet_retina_tiles
from apps.websockets.app import app as app_websockets
from gallery.app import app as app_gallery
from starlette.applications import Starlette
from contextlib import AsyncExitStack, asynccontextmanager
from fastapi import FastAPI
from starlette.routing import Mount

# Include nested lifespans for Starlette 
# https://github.com/encode/starlette/issues/649
@asynccontextmanager
async def nested_lifespan(app):
    async with AsyncExitStack() as stack:
        for route in app.routes:
            if isinstance(route, Mount) and (isinstance(route.app, FastAPI) or isinstance(route.app, Starlette)):
                await stack.enter_async_context(
                    route.app.router.lifespan_context(route.app), 
                )
        yield

app = Starlette(lifespan=nested_lifespan)
app.mount("/dark_theme/", app_dark_theme)
app.mount("/fastapi/", app_fastapi)
app.mount("/fastapi_users/", app_fastapi_users, name="fastapi_users")
app.mount("/input_search/", app_input_search)
app.mount("/leaflet_live_positions/", app_leaflet_live_positions)
app.mount("/leaflet_retina_tiles/", app_leaflet_retina_tiles)
app.mount("/websockets/", app_websockets)
app.mount("/", app_gallery)

