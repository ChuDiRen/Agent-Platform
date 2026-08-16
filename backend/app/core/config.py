from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator, model_validator
from pathlib import Path
from typing import Optional, Union

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = ConfigDict(case_sensitive=True)

    PROJECT_NAME: str = "My FastAPI App"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "sqlite:///./test.db"

    # JWT — 生产环境必须通过环境变量 SECRET_KEY 覆盖（见 validate_production_defaults）
    SECRET_KEY: str = "dev-only-insecure-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: Union[list[str], str] = ["*"]

    # Celery / Redis — 生产环境必须通过环境变量覆盖（默认仅本机、无凭据）
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    CELERY_BROKER_CONNECTION_TIMEOUT: float = 5.0
    CELERY_TASK_ALWAYS_EAGER: bool = False

    # Agent model provider — API Key 不在代码中提供，必须通过环境变量 AGENT_MODEL_API_KEY 配置
    AGENT_MODEL_SPEC: str = "openai:mimo-v2.5-pro"
    AGENT_MODEL_BASE_URL: str = "https://token-plan-sgp.xiaomimimo.com/v1"
    AGENT_MODEL_API_KEY: str = ""

    # 启动 seed 管理员（仅空库时创建；生产环境必须覆盖 ADMIN_PASSWORD）
    ADMIN_EMAIL: str = "admin@qq.com"
    ADMIN_PASSWORD: str = "admin123456"

    # 上传限制
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (init_settings, env_settings)

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            normalized = v.lower()
            if normalized in ("true", "1", "yes", "on"):
                return True
            if normalized in ("false", "0", "no", "off"):
                return False
            return True
        return bool(v)

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            value = v.strip()
            if value.startswith("["):
                return v
            return [item.strip() for item in value.split(",") if item.strip()]
        return v

    @property
    def cors_origins(self) -> list[str]:
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [item.strip() for item in self.BACKEND_CORS_ORIGINS.split(",") if item.strip()]
        return self.BACKEND_CORS_ORIGINS

    @model_validator(mode="after")
    def validate_production_defaults(self):
        if self.DEBUG:
            return self
        if self.SECRET_KEY in {"", "dev-only-insecure-secret-key", "change-me-in-production-please"}:
            raise ValueError("生产模式必须配置安全的 SECRET_KEY")
        if self.cors_origins == ["*"]:
            raise ValueError("生产模式不允许使用通配 CORS")
        if not self.AGENT_MODEL_API_KEY or self.AGENT_MODEL_API_KEY in {"change-me", "not-used", "placeholder"}:
            raise ValueError("生产模式必须配置有效的 Agent 模型 API Key")
        if not self.ADMIN_PASSWORD or self.ADMIN_PASSWORD == "admin123456":
            raise ValueError("生产模式必须覆盖默认管理员密码 ADMIN_PASSWORD")
        return self


settings = Settings()
