"""C's chat request boundary and conversation helpers."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Protocol

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings


ALLOWED_MODES = {"q1", "q4", "q5", "q6", "free"}
logger = logging.getLogger(__name__)


class CompletedChat(Protocol):
    question: str
    answer: str | None
    status: str


def build_messages(recent_first: Sequence[CompletedChat], question: str) -> list[dict[str, str]]:
    """Turn up to five successful Q/A pairs into chronological LLM messages."""
    completed = [chat for chat in recent_first if chat.status == "success" and chat.answer]
    messages: list[dict[str, str]] = []
    for chat in reversed(completed[:5]):
        messages.extend(
            [
                {"role": "user", "content": chat.question},
                {"role": "assistant", "content": chat.answer or ""},
            ]
        )
    messages.append({"role": "user", "content": question})
    return messages


class ChatRequest(BaseModel):
    mode: str
    message: str
    keyword: str | None = None

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
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise ValueError("질문에 사용할 수 없는 문자가 있어요.") from None
        return value

    @field_validator("keyword")
    @classmethod
    def require_valid_keyword(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        value = value.strip()
        if len(value) > 50:
            raise ValueError("분석 키워드는 50자 이하로 입력해 주세요.")
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise ValueError("키워드에 사용할 수 없는 문자가 있어요.") from None
        return value


def create_router(require_login, get_db) -> APIRouter:
    """Register C's route with A's actual authentication and DB dependencies."""
    from app.models.chat import Chat
    from app.services.llm import AIServiceError, AITimeoutError, ask_llm
    from app.services.scenarios import q5, q6

    router = APIRouter()

    @router.post("/api/chat")
    async def post_chat(body: ChatRequest, user=Depends(require_login), db: Session = Depends(get_db)):
        logger.info("request_received user_id=%s", user.id)
        previous = (
            db.query(Chat)
            .filter(Chat.user_id == user.id, Chat.status == "success", Chat.answer.is_not(None))
            .order_by(Chat.created_at.desc(), Chat.id.desc())
            .limit(5)
            .all()
        )
        messages = build_messages(previous, body.message)

        if body.mode == "q5":
            system = await q5.build_prompt(body.message)
        elif body.mode == "q6":
            system = await q6.build_prompt(body.message)
        elif body.mode == "q1":
            from app.services.scenarios import q1

            system = await q1.build_prompt(body.message)
        elif body.mode == "q4":
            from app.services.scenarios import q3

            system = await q3.build_prompt(body.message, body.keyword)
        else:
            system = (
                "당신은 경제·AI 숏폼 제작자의 도우미입니다. 한국어로 간결하게 답하세요. "
                "주어진 자료가 없으면 최신 이슈·검색 추이를 확인하지 못했다고 밝히고 지어내지 마세요."
            )

        answer: str | None = None
        status = "success"
        try:
            logger.info("ai_call_start user_id=%s mode=%s", user.id, body.mode)
            answer = await ask_llm(system, messages)
            logger.info("ai_call_success user_id=%s mode=%s", user.id, body.mode)
        except AITimeoutError:
            status = "timeout"
            logger.warning("ai_call_fail user_id=%s mode=%s reason=timeout", user.id, body.mode)
        except AIServiceError:
            status = "error"
            logger.warning("ai_call_fail user_id=%s mode=%s reason=provider", user.id, body.mode)

        chat = Chat(user_id=user.id, mode=body.mode, question=body.message, answer=answer, status=status)
        try:
            db.add(chat)
            db.flush()
            chat_id = chat.id
            db.commit()
            logger.info("db_save_success user_id=%s chat_id=%s status=%s", user.id, chat_id, status)
        except SQLAlchemyError:
            db.rollback()
            logger.exception("db_save_fail user_id=%s mode=%s", user.id, body.mode)
            return JSONResponse(
                status_code=500,
                content={"error": "DB_ERROR", "message": "대화 기록을 저장하지 못했습니다."},
            )

        if status == "timeout":
            return JSONResponse(
                status_code=504,
                content={"error": "AI_TIMEOUT", "message": "현재 응답이 지연되고 있어요. 잠시 후 다시 시도해 주세요."},
            )
        if status == "error":
            return JSONResponse(
                status_code=502,
                content={"error": "AI_ERROR", "message": "AI 응답을 받지 못했습니다. 잠시 후 다시 시도해 주세요."},
            )
        return {"chat_id": chat_id, "answer": answer}

    @router.get("/api/me")
    def me(user=Depends(require_login)):
        return {
            "id": user.id,
            "email": user.email,
            "trend_configured": bool(settings.NAVER_CLIENT_ID and settings.NAVER_CLIENT_SECRET),
            "llm_configured": bool(settings.LLM_API_KEY),
        }

    return router
