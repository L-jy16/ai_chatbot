import asyncio
import logging
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import require_login
from app.errors import APIError
from app.models import Chat, User
from app.services import llm
from app.services.scenarios import q1, q2, q3, q4, q5

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    mode: Literal["q1", "q2", "q3", "q4", "q5"] = "q1"
    message: str
    keyword: str | None = None

    @field_validator("message")
    @classmethod
    def valid_message(cls, value: str) -> str:
        value = value.strip()
        if not 1 <= len(value) <= 500:
            raise ValueError("질문은 1~500자로 입력해 주세요.")
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise ValueError("질문에 사용할 수 없는 문자가 있어요.") from None
        return value

    @field_validator("keyword")
    @classmethod
    def valid_keyword(cls, value: str | None) -> str | None:
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


def save_chat(db: Session, chat: Chat) -> None:
    try:
        db.add(chat)
        db.commit()
        db.refresh(chat)
    except SQLAlchemyError:
        db.rollback()
        logger.error("db_save_fail user_id=%s", chat.user_id)
        raise APIError(500, "DB_ERROR", "대화 기록을 저장하지 못했어요. 잠시 후 다시 시도해 주세요.") from None
    logger.info("db_save_success user_id=%s chat_id=%s status=%s", chat.user_id, chat.id, chat.status)


@router.post("/chat")
async def chat(body: ChatRequest, user: User = Depends(require_login), db: Session = Depends(get_db)):
    logger.info("request_received user_id=%s mode=%s", user.id, body.mode)
    previous = list(db.scalars(
        select(Chat).where(Chat.user_id == user.id, Chat.status == "success")
        .order_by(Chat.id.desc()).limit(5)
    ))
    messages = []
    for item in reversed(previous):
        messages.extend([
            {"role": "user", "content": item.question},
            {"role": "assistant", "content": item.answer},
        ])
    messages.append({"role": "user", "content": body.message})
    record = Chat(user_id=user.id, mode=body.mode, question=body.message, status="error")
    try:
        # 트렌드 조회 전체에도 상한을 둔다. 동기 HTTP는 시나리오에서 스레드로 분리한다.
        if body.mode == "q1":
            prompt_task = q1.build_prompt(body.message)
        elif body.mode == "q2":
            prompt_task = q2.build_prompt(body.message, context=[item.question for item in reversed(previous)])
        else:
            scenario = {"q3": q3, "q4": q4, "q5": q5}[body.mode]
            prompt_task = scenario.build_prompt(body.message, body.keyword)
        system = await asyncio.wait_for(prompt_task, timeout=settings.NAVER_TIMEOUT_SECONDS * 4 + 2)
        logger.info("ai_call_start user_id=%s mode=%s", user.id, body.mode)
        record.answer = await llm.ask_llm(system, messages)
        record.status = "success"
        logger.info("ai_call_success user_id=%s", user.id)
    except (llm.AITimeoutError, asyncio.TimeoutError):
        record.status = "timeout"
        logger.warning("ai_call_fail user_id=%s status=timeout", user.id)
        save_chat(db, record)
        raise APIError(504, "AI_TIMEOUT", "현재 응답이 지연되고 있어요. 잠시 후 다시 시도해 주세요.") from None
    except llm.AIError:
        logger.warning("ai_call_fail user_id=%s status=error", user.id)
        save_chat(db, record)
        raise APIError(502, "AI_ERROR", "AI에 연결하지 못했어요. 서버의 API 키와 모델 설정을 확인해 주세요.") from None
    save_chat(db, record)
    return {"chat_id": record.id, "answer": record.answer}


@router.get("/me")
def me(user: User = Depends(require_login)):
    return {
        "id": user.id, "email": user.email,
        "trend_configured": bool(settings.NAVER_CLIENT_ID and settings.NAVER_CLIENT_SECRET),
        "llm_configured": bool(settings.LLM_API_KEY and settings.LLM_MODEL),
    }
