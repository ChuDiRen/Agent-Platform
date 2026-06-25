from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from pathlib import Path
from typing import Optional

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = ConfigDict(case_sensitive=True)

    PROJECT_NAME: str = "My FastAPI App"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "sqlite:///./test.db"

    # JWT
    SECRET_KEY: str = "change-me-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # Celery / Redis
    CELERY_BROKER_URL: str = "redis://:admin123456@192.168.111.128:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://:admin123456@192.168.111.128:6379/1"
    CELERY_BROKER_CONNECTION_TIMEOUT: float = 5.0
    CELERY_TASK_ALWAYS_EAGER: bool = False

    # Agent model provider
    AGENT_MODEL_SPEC: str = "openai:mimo-v2.5-pro"
    AGENT_MODEL_BASE_URL: str = "https://token-plan-sgp.xiaomimimo.com/v1"
    AGENT_MODEL_API_KEY: str = "tp-s5516suwc3a233b2gyrln9ovveptfd7chvwe582kwk849lrj"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (init_settings,)

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)


settings = Settings()
