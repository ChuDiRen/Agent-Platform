from app.core.config import Settings


def test_model_provider_config_is_code_defined(monkeypatch):
    monkeypatch.setenv("AGENT_MODEL_SPEC", "openai:not-used")
    monkeypatch.setenv("AGENT_MODEL_BASE_URL", "https://not-used.example/v1")
    monkeypatch.setenv("AGENT_MODEL_API_KEY", "not-used")

    settings = Settings()

    assert settings.AGENT_MODEL_SPEC == "openai:mimo-v2.5-pro"
    assert settings.AGENT_MODEL_BASE_URL == "https://token-plan-sgp.xiaomimimo.com/v1"
    assert settings.AGENT_MODEL_API_KEY.startswith("tp-")


def test_core_runtime_config_is_code_defined(monkeypatch):
    monkeypatch.setenv("PROJECT_NAME", "not-used")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///not-used.db")
    monkeypatch.setenv("SECRET_KEY", "not-used")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://not-used:6379/0")
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://not-used:6379/1")
    monkeypatch.setenv("CELERY_BROKER_CONNECTION_TIMEOUT", "1")
    monkeypatch.setenv("DEBUG", "false")

    settings = Settings()

    assert settings.PROJECT_NAME == "My FastAPI App"
    assert settings.DATABASE_URL == "sqlite:///./test.db"
    assert settings.SECRET_KEY == "change-me-in-production-please"
    assert settings.CELERY_BROKER_URL == "redis://:admin123456@192.168.111.128:6379/0"
    assert settings.CELERY_RESULT_BACKEND == "redis://:admin123456@192.168.111.128:6379/1"
    assert settings.CELERY_BROKER_CONNECTION_TIMEOUT == 5.0
    assert settings.DEBUG is True
