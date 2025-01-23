from shiny import reactive
from httpx import AsyncClient
from ..config import settings
from urllib.parse import urljoin

def get_api_client(session):

    def get_base_url(session):
        # Use ClientData to get URL components to build the base url.
        # These values are from the browser's perspective, so neither
        # HTTP proxies nor Shiny Server will affect these values.
        # Seems to be the most reliable method of solving subpaths etc.
        # Wrap in isolate to avoid taking a reactive dependency.
        # See ClientData section in the documentation:
        # https://shiny.posit.co/r/reference/shiny/latest/session.html
        with reactive.isolate():
            protocol = session.input[".clientdata_url_protocol"]()
            hostname = session.input[".clientdata_url_hostname"]()
            port = session.input[".clientdata_url_port"]()
    
        if port:
            url = urljoin(f"{protocol}//{hostname}:{port}", settings.path_root)
        else:
            url = urljoin(f"{protocol}//{hostname}", settings.path_root)

        return url

    base_url = get_base_url(session)
    return AsyncClient(base_url=base_url)

