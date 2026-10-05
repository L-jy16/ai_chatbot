"""D-owned page routes. SessionMiddleware and authentication belong to A."""
from pathlib import Path
from typing import Any, Callable

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


def session_user_id(request: Request) -> int | None:
    value = request.session.get("user_id")
    return value if type(value) is int and value > 0 else None


def render(request: Request, name: str, active_page: str, *, signed_in: bool):
    response = templates.TemplateResponse(
        request=request,
        name=name,
        context={"signed_in": signed_in,
                 "active_page": active_page,
                 "demo_mode": getattr(request.app.state, "ui_demo_mode", False),
                 "backend_pending": getattr(request.app.state, "ui_backend_pending", False)},
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; "
        "base-uri 'self'; form-action 'self'"
    )
    return response


def create_pages_router(*, get_current_user: Callable | None = None) -> APIRouter:
    """Use A's DB-backed identity in the real app; session-only in the demo."""
    router = APIRouter(include_in_schema=False)
    current_user = get_current_user or session_user_id

    @router.get("/")
    def chat_page(request: Request, user: Any = Depends(current_user)):
        if user is None:
            return RedirectResponse("/login", status_code=303)
        return render(request, "chat.html", "chat", signed_in=True)

    @router.get("/history")
    def history_page(request: Request, user: Any = Depends(current_user)):
        if user is None:
            return RedirectResponse("/login", status_code=303)
        return render(request, "history.html", "history", signed_in=True)

    @router.get("/login")
    def login_page(request: Request, user: Any = Depends(current_user)):
        if user is not None:
            return RedirectResponse("/", status_code=303)
        return render(request, "login.html", "login", signed_in=False)

    @router.get("/signup")
    def signup_page(request: Request, user: Any = Depends(current_user)):
        if user is not None:
            return RedirectResponse("/", status_code=303)
        return render(request, "signup.html", "signup", signed_in=False)

    return router


router = create_pages_router()
