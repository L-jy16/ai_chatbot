"""D-owned page routes. SessionMiddleware and authentication belong to A."""
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


def session_user_id(request: Request) -> int | None:
    value = request.session.get("user_id")
    return value if type(value) is int and value > 0 else None


def render(request: Request, name: str, active_page: str):
    response = templates.TemplateResponse(
        request=request,
        name=name,
        context={"signed_in": session_user_id(request) is not None,
                 "active_page": active_page,
                 "demo_mode": getattr(request.app.state, "ui_demo_mode", False)},
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; "
        "base-uri 'self'; form-action 'self'"
    )
    return response


@router.get("/")
def chat_page(request: Request):
    if session_user_id(request) is None:
        return RedirectResponse("/login", status_code=303)
    return render(request, "chat.html", "chat")


@router.get("/history")
def history_page(request: Request):
    if session_user_id(request) is None:
        return RedirectResponse("/login", status_code=303)
    return render(request, "history.html", "history")


@router.get("/login")
def login_page(request: Request):
    if session_user_id(request) is not None:
        return RedirectResponse("/", status_code=303)
    return render(request, "login.html", "login")


@router.get("/signup")
def signup_page(request: Request):
    if session_user_id(request) is not None:
        return RedirectResponse("/", status_code=303)
    return render(request, "signup.html", "signup")
