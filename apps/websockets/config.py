from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    entur_wss_url: str
    entur_wss_client_name: str

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()