import pytest
from pydantic import ValidationError

from app.config import Settings

OPTIONAL_KEYS = [
    "DATABASE_URL",
    "NAVER_CLIENT_ID",
    "NAVER_CLIENT_SECRET",
    "LLM_API_KEY",
    "LLM_MODEL",
    "LLM_TIMEOUT_SECONDS",
]


def test_secret_key_is_required(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_empty_secret_key_is_rejected(monkeypatch):
    # .env.example을 복사만 하고 값을 안 채운 경우
    monkeypatch.setenv("SECRET_KEY", "")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_optional_settings_have_defaults(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "x" * 32)
    for key in OPTIONAL_KEYS:
        monkeypatch.delenv(key, raising=False)

    settings = Settings(_env_file=None)

    assert settings.DATABASE_URL == "sqlite:///./app.db"
    assert settings.NAVER_CLIENT_ID == ""
    assert settings.NAVER_CLIENT_SECRET == ""
    assert settings.LLM_API_KEY == ""
    assert settings.LLM_MODEL == ""
    assert settings.LLM_TIMEOUT_SECONDS == 50  # gpt-5-mini 추론 응답이 30초를 넘는 경우가 있다
