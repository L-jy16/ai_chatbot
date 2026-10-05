"""One registration call for D's routes and static assets."""
from pathlib import Path
from typing import Callable

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers.logs import create_logs_router
from app.routers.pages import router as pages_router


def install_ui(app: FastAPI, *, require_login: Callable, get_db: Callable, chat_model: type) -> None:
    """Requires SessionMiddleware; get_db must yield a synchronous Session."""
    if getattr(app.state, "ui_installed", False):
        raise RuntimeError("install_ui must be called only once")
    reserved = {"/", "/login", "/signup", "/history", "/api/me/chats", "/static"}
    conflicts = reserved.intersection(getattr(route, "path", "") for route in app.routes)
    if conflicts:
        raise RuntimeError(f"D route paths already registered: {sorted(conflicts)}")
    app.mount("/static", StaticFiles(directory=str(Path(__file__).resolve().parent / "static")), name="static")
    app.include_router(pages_router)
    app.include_router(create_logs_router(require_login=require_login, get_db=get_db, chat_model=chat_model))
    app.state.ui_installed = True
