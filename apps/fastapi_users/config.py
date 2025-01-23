from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    path_proxy: Optional[str] = None                    # If behind a reverse proxy (e.g. ... .shinyapps.io/{path}) provide '/{path}' for resolving URLs, else leave blank ''
    path_nested_mount: Optional[str] = "fastapi_users"  # If app is served as a nested starlette app (e.g. 'shiny run app' in this repo), provide {name} (fastapi_users) of nested app for resolving URLs. Otherwise (shiny run apps.fastapi_users.app) leave this blank.
    db_url: str
    jwt_secret: str
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "allow"
    
    @property
    def path_root(self) -> str:

        proxy_path = (self.path_proxy or "").rstrip("/")
        nested_path = (self.path_nested_mount or "").lstrip("/")

        path = f"{proxy_path}/{nested_path}" if nested_path else proxy_path
        
        return path

settings = Settings()