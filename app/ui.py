"""One registration call for D's routes and static assets."""
from pathlib import Path
from typing import Callable

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.routers.logs import create_logs_router
from app.routers.pages import create_pages_router


def install_ui(app: FastAPI, *, require_login: Callable, get_db: Callable,
               chat_model: type | None = None, get_current_user: Callable | None = None) -> None:
    """Requires SessionMiddleware; get_db must yield a synchronous Session."""
    if getattr(app.state, "ui_installed", False):
        raise RuntimeError("install_ui must be called only once")
    reserved = {"/", "/login", "/signup", "/history", "/api/me/chats", "/static"}
    if chat_model is None:
        reserved.add("/api/chat")
    conflicts = reserved.intersection(getattr(route, "path", "") for route in app.routes)
    if conflicts:
        raise RuntimeError(f"D route paths already registered: {sorted(conflicts)}")
    app.mount("/static", StaticFiles(directory=str(Path(__file__).resolve().parent / "static")), name="static")
    app.include_router(create_pages_router(get_current_user=get_current_user))
    if chat_model is not None:
        app.include_router(create_logs_router(require_login=require_login, get_db=get_db, chat_model=chat_model))
    else:
        @app.post("/api/chat", tags=["pending"])
        def pending_chat(user=Depends(require_login)):
            return JSONResponse(status_code=503, content={"error": "CHAT_NOT_READY", "message": "채팅 기능을 준비 중입니다. 잠시 후 다시 이용해 주세요."})

        @app.get("/api/me/chats", tags=["pending"])
        def pending_history(user=Depends(require_login)):
            return JSONResponse(status_code=503, content={"error": "HISTORY_NOT_READY", "message": "대화 기록 기능을 준비 중입니다. 잠시 후 다시 이용해 주세요."})
    app.state.ui_backend_pending = chat_model is None
    app.state.ui_installed = True
