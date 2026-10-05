"""User-scoped history router; inject A's auth/DB and C's Chat model."""
from datetime import datetime
import logging
from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, model_validator
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ChatLog(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    mode: str
    question: str
    answer: str | None
    status: str
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_mode(cls, value):
        # 기존 DB의 Q4 타이밍을 새 UI의 '새로운 각도'로 오표시하지 않는다.
        if getattr(value, "scenario_version", 2) == 1:
            row = {name: getattr(value, name) for name in cls.model_fields}
            row["mode"] = {"q4": "q3", "q5": "q4", "q6": "q5"}.get(row["mode"], row["mode"])
            return row
        return value


def authenticated_user_id(user: Any) -> int:
    """A may return an integer ID, User instance or {'id': integer}."""
    value = user if type(user) is int else user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
    if type(value) is not int or value <= 0:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    return value


def create_logs_router(*, require_login: Callable, get_db: Callable, chat_model: type) -> APIRouter:
    router = APIRouter(prefix="/api/me", tags=["my-chats"])

    @router.get("/chats", response_model=list[ChatLog])
    def my_chats(
        response: Response,
        limit: int = Query(default=20, ge=1, le=100),
        user: Any = Depends(require_login),
        db: Session = Depends(get_db),
    ):
        user_id = authenticated_user_id(user)
        response.headers["Cache-Control"] = "no-store"
        statement = (
            select(chat_model)
            .where(chat_model.user_id == user_id)
            .order_by(chat_model.created_at.desc(), chat_model.id.desc())
            .limit(limit)
        )
        try:
            return db.execute(statement).scalars().all()
        except SQLAlchemyError:
            logger.exception("chat_history_read_failed user_id=%s", user_id)
            raise HTTPException(status_code=503, detail="기록을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.") from None

    return router
