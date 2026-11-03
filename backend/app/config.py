from functools import lru_cache
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MineGuard AI"
    environment: str = "development"
    database_url: str = "sqlite:///./mineguard.db"
    jwt_secret: SecretStr = SecretStr("development-only-secret-change-me-32-bytes")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=60, gt=0)
    upload_directory: str = "data/uploads"
    ai_service_url: str = "http://localhost:8001"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    ai_mode: str = "DEMO_SIMULATION"
    ocr_mode: str = "DEMO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        origins = self.cors_origin_list
        if not origins or "*" in origins:
            raise ValueError("CORS_ORIGINS must contain explicit origins and cannot include '*'.")

        for origin in origins:
            parsed = urlsplit(origin)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.path:
                raise ValueError("CORS_ORIGINS entries must be HTTP(S) origins without paths.")

        if self.environment.lower() in {"production", "prod"}:
            secret = self.jwt_secret.get_secret_value()
            secret_lower = secret.lower()
            if (
                len(secret.encode("utf-8")) < 32
                or any(marker in secret_lower for marker in ("development-only", "replace-with", "change-me", "placeholder"))
            ):
                raise ValueError("Production requires a unique JWT_SECRET of at least 32 bytes.")
            if any(not origin.startswith("https://") for origin in origins):
                raise ValueError("Production CORS origins must use HTTPS.")

        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
