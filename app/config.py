from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """.env 파일 또는 환경 변수에서 읽는 앱 설정."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # A: 세션 쿠키 서명 키 (필수, 빈 값 금지)
    SECRET_KEY: str = Field(min_length=16)
    # A: DB 연결 주소
    DATABASE_URL: str = "sqlite:///./app.db"

    # B: 네이버 API
    NAVER_CLIENT_ID: str = ""
    NAVER_CLIENT_SECRET: str = ""
    NAVER_TIMEOUT_SECONDS: float = Field(default=5, gt=0)

    # C: LLM API
    LLM_API_KEY: str = ""
    LLM_MODEL: str = ""
    LLM_BASE_URL: str = "https://copa.codyssey.kr/v1"
    LLM_TIMEOUT_SECONDS: float = Field(default=50, gt=0)  # 추론 모델 응답 여유, 브라우저 제한(65초)보다 짧게


settings = Settings()
