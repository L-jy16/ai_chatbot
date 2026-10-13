"""운영자용 DB 조회 화면(/admin). 조회만 하며 ADMIN_USERNAME·ADMIN_PASSWORD Basic 인증 뒤에 둔다.

계정이 없으면 라우터를 만들지 않아 404가 된다. 개인정보를 줄이려고 이메일은 일부만,
질문은 앞부분만, 답변은 글자 수만 보여 준다.
"""
from typing import Callable, Literal

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.basic_auth import basic_auth_guard
from app.models import Chat, User
from app.routers.pages import templates

STATUSES = ("success", "timeout", "error")
QUESTION_PREVIEW = 80
RECENT_USERS = 10


def mask_email(email: str) -> str:
    """앞 두 글자(로컬 부분이 짧으면 한 글자)와 도메인만 남긴다."""
    local, _, domain = email.partition("@")
    keep = 2 if len(local) > 2 else 1
    return f"{local[:keep]}***@{domain}"


def preview(text: str, size: int = QUESTION_PREVIEW) -> str:
    return text if len(text) <= size else text[:size] + "…"


def collect_admin_data(db: Session, status: str | None, limit: int) -> dict:
    """요약 수치, 최근 대화(최신순, 상태 필터), 최근 가입자를 모은다."""
    by_status = dict(db.execute(select(Chat.status, func.count()).group_by(Chat.status)).all())
    by_mode = dict(db.execute(select(Chat.mode, func.count()).group_by(Chat.mode).order_by(Chat.mode)).all())
    summary = {
        "users": db.scalar(select(func.count()).select_from(User)),
        "chats": db.scalar(select(func.count()).select_from(Chat)),
        # created_at은 SQLite의 UTC 시각이라 같은 기준(datetime('now'))으로 비교한다.
        "chats_24h": db.scalar(select(func.count()).select_from(Chat)
                               .where(Chat.created_at >= func.datetime("now", "-1 day"))),
        "by_status": {name: by_status.get(name, 0) for name in STATUSES},
        "by_mode": by_mode,
    }
    query = select(Chat, User.email).join(User, Chat.user_id == User.id).order_by(Chat.id.desc()).limit(limit)
    if status:
        query = query.where(Chat.status == status)
    chats = [{"id": chat.id, "created_at": chat.created_at, "user": mask_email(email), "mode": chat.mode,
              "status": chat.status, "question": preview(chat.question), "answer_length": len(chat.answer or "")}
             for chat, email in db.execute(query).all()]
    users = [{"id": user.id, "email": mask_email(user.email), "created_at": user.created_at}
             for user in db.scalars(select(User).order_by(User.id.desc()).limit(RECENT_USERS))]
    return {"summary": summary, "chats": chats, "users": users, "status": status, "limit": limit}


def create_admin_router(*, get_db: Callable, username: str, password: str) -> APIRouter | None:
    """계정이 둘 다 있을 때만 /admin 라우터를 만든다. 인증은 쿼리 검증보다 먼저 확인된다."""
    guard = basic_auth_guard(username, password)
    if guard is None:
        return None

    router = APIRouter(include_in_schema=False, dependencies=[Depends(guard)])

    @router.get("/admin")
    def admin_page(request: Request,
                   status: Literal["success", "timeout", "error"] | None = None,
                   limit: int = Query(50, ge=1, le=200),
                   db: Session = Depends(get_db)):
        context = collect_admin_data(db, status, limit) | {"statuses": STATUSES, "preview_size": QUESTION_PREVIEW}
        response = templates.TemplateResponse(request=request, name="admin.html", context=context)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'none'; style-src 'self'; frame-ancestors 'none'; "
            "base-uri 'self'; form-action 'self'"
        )
        return response

    return router
