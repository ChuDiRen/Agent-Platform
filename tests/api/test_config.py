import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_model_provider_config_has_code_defaults(monkeypatch):
    monkeypatch.delenv("AGENT_MODEL_SPEC", raising=False)
    monkeypatch.delenv("AGENT_MODEL_BASE_URL", raising=False)
    monkeypatch.delenv("AGENT_MODEL_API_KEY", raising=False)

    settings = Settings()

    assert settings.AGENT_MODEL_SPEC == "openai:mimo-v2.5-pro"
    assert settings.AGENT_MODEL_BASE_URL == "https://token-plan-sgp.xiaomimimo.com/v1"
    assert settings.AGENT_MODEL_API_KEY.startswith("tp-")


def test_core_runtime_config_has_code_defaults(monkeypatch):
    for key in [
        "PROJECT_NAME",
        "DATABASE_URL",
        "SECRET_KEY",
        "CELERY_BROKER_URL",
        "CELERY_RESULT_BACKEND",
        "CELERY_BROKER_CONNECTION_TIMEOUT",
        "DEBUG",
    ]:
        monkeypatch.delenv(key, raising=False)

    settings = Settings()

    assert settings.PROJECT_NAME == "My FastAPI App"
    assert settings.DATABASE_URL == "sqlite:///./test.db"
    assert settings.SECRET_KEY == "change-me-in-production-please"
    assert settings.CELERY_BROKER_URL == "redis://:admin123456@192.168.111.128:6379/0"
    assert settings.CELERY_RESULT_BACKEND == "redis://:admin123456@192.168.111.128:6379/1"
    assert settings.CELERY_BROKER_CONNECTION_TIMEOUT == 5.0
    assert settings.DEBUG is True


def test_environment_can_override_runtime_config(monkeypatch):
    monkeypatch.setenv("PROJECT_NAME", "Agent Platform")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///runtime.db")
    monkeypatch.setenv("SECRET_KEY", "runtime-secret")
    monkeypatch.setenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:4173")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
    monkeypatch.setenv("CELERY_BROKER_CONNECTION_TIMEOUT", "1")
    monkeypatch.setenv("DEBUG", "true")

    settings = Settings()

    assert settings.PROJECT_NAME == "Agent Platform"
    assert settings.DATABASE_URL == "sqlite:///runtime.db"
    assert settings.SECRET_KEY == "runtime-secret"
    assert settings.cors_origins == ["http://localhost:3000", "http://localhost:4173"]
    assert settings.CELERY_BROKER_URL == "redis://localhost:6379/0"
    assert settings.CELERY_RESULT_BACKEND == "redis://localhost:6379/1"
    assert settings.CELERY_BROKER_CONNECTION_TIMEOUT == 1.0
    assert settings.DEBUG is True


def test_production_rejects_unsafe_defaults(monkeypatch):
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("BACKEND_CORS_ORIGINS", raising=False)

    with pytest.raises(ValidationError, match="生产模式必须配置安全的 SECRET_KEY"):
        Settings()


def test_production_accepts_safe_overrides(monkeypatch):
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("SECRET_KEY", "safe-production-secret")
    monkeypatch.setenv("BACKEND_CORS_ORIGINS", "https://agent-platform.example.com")
    monkeypatch.setenv("AGENT_MODEL_API_KEY", "prod-model-key")

    settings = Settings()

    assert settings.DEBUG is False
    assert settings.SECRET_KEY == "safe-production-secret"
    assert settings.cors_origins == ["https://agent-platform.example.com"]
    assert settings.AGENT_MODEL_API_KEY == "prod-model-key"