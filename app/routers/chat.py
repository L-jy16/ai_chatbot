"""C's chat request boundary and conversation helpers."""

from pydantic import BaseModel, field_validator


ALLOWED_MODES = {"q1", "q4", "q5", "q6", "free"}


class ChatRequest(BaseModel):
    mode: str
    message: str

    @field_validator("mode", "message", mode="before")
    @classmethod
    def require_text(cls, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("문자열로 입력해 주세요.")
        return value.strip()

    @field_validator("mode")
    @classmethod
    def require_supported_mode(cls, value: str) -> str:
        if value not in ALLOWED_MODES:
            raise ValueError("지원하지 않는 모드입니다.")
        return value

    @field_validator("message")
    @classmethod
    def require_valid_question(cls, value: str) -> str:
        if not 1 <= len(value) <= 500:
            raise ValueError("질문은 1~500자로 입력해 주세요.")
        return value
