import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app import models  # noqa: F401  모델을 Base에 등록해 create_all 대상이 되게 한다
from app.config import settings
from app.database import Base, engine, get_db, upgrade_chat_schema
from app.dependencies import get_current_user, require_login
from app.docs import install_docs
from app.errors import register_error_handlers
from app.models.chat import Chat
from app.routers import auth
from app.routers.chat import create_router
from app.ui import install_ui

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    upgrade_chat_schema(engine)
    Base.metadata.create_all(bind=engine)
    yield


# 기본 문서 경로는 끄고, 계정이 설정된 경우에만 Basic 인증 뒤에 연다(app/docs.py).
app = FastAPI(title="경제 숏폼 트렌드 챗봇", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax",
    https_only=False,  # VM에 HTTP로 배포해도 쿠키가 전송되도록
)
register_error_handlers(app)
install_docs(app, settings.DOCS_USERNAME, settings.DOCS_PASSWORD)
app.include_router(auth.router)
app.include_router(create_router(require_login, get_db))
install_ui(
    app,
    require_login=require_login,
    get_db=get_db,
    get_current_user=get_current_user,
    chat_model=Chat,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
