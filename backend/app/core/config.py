from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import Optional


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    PROJECT_NAME: str = "FastAPI App"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # 数据库
    DATABASE_URL: str = "sqlite:///./test.db"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)


settings = Settings()
