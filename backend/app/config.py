from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MineGuard AI"
    environment: str = "development"
    database_url: str = "sqlite:///./mineguard.db"
    jwt_secret: str = "development-only-secret-change-me-32-bytes"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    upload_directory: str = "data/uploads"
    ai_service_url: str = "http://localhost:8001"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    ai_mode: str = "DEMO_SIMULATION"
    ocr_mode: str = "DEMO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
