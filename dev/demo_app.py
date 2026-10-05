"""Local-only UI harness. Never deploy this mock in place of app.main."""
import asyncio
from datetime import datetime, timedelta
import logging
import secrets
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.middleware.sessions import SessionMiddleware

from app.routers.pages import session_user_id
from app.ui import install_ui

logger = logging.getLogger(__name__)


class DemoBase(DeclarativeBase):
    pass


class DemoChat(DemoBase):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    mode: Mapped[str] = mapped_column(String)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime)


class Credentials(BaseModel):
    email: str
    password: str


class ChatInput(BaseModel):
    mode: Literal["q1", "q4", "q5", "q6"]
    message: str = Field(min_length=1, max_length=500)

    @field_validator("message")
    @classmethod
    def nonempty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("empty question")
        return value


ANSWERS = {
    "q1": "[예시 응답 · 실시간 데이터 미연결]\n\n추천 주제: AI 투자 뉴스, 숫자 뒤에 숨은 비용은?\n\n후킹: ‘AI에 돈이 몰린다는데, 전기 요금은 누가 낼까요?’\n구성: 투자 배경 → 데이터센터 비용 → 시청자가 확인할 지표.\n\n실제 추천에는 B의 뉴스·검색 추이와 C의 AI 응답을 연결해야 합니다.",
    "q4": "[예시 응답 · 실제 추이 판정 아님]\n\n타이밍을 판단하려면 최근 검색 추이와 과거 구간을 비교해야 해요.\n상승이면 지금 올리기, 정점이면 새 관점 찾기, 하락이면 후속 이슈 기다리기를 검토합니다.\n\n질문의 주제에 대한 실제 데이터는 아직 연결되지 않았습니다.",
    "q5": "[예시 응답 · 실시간 데이터 미연결]\n\n1. 반전: 투자 증가가 수익 증가로 이어질까?\n2. 비교: 대기업과 작은 기업의 AI 도입 비용.\n3. 논쟁: 생산성 향상인가, 비용의 이동인가?\n4. 정보: 실적 발표에서 확인할 세 가지 지표.\n5. 경험: 실제 작업 시간을 줄인 사례와 한계.\n\n예시 추천: 4번. 시청자가 직접 확인할 수 있는 질문으로 구성하세요.",
    "q6": "[예시 응답 · 실시간 데이터 미연결]\n\n1편: 현상의 원인 - 왜 바뀌었을까?\n2편: 생활의 변화 - 내 지출에는 어떤 영향이 있을까?\n3편: 다음에 볼 지표 - 무엇을 확인해야 할까?\n\n다음 편 예시: 2편. 어제 영상의 결론을 짧게 되짚고 생활 속 사례로 이어가세요.",
}


def create_demo_app() -> FastAPI:
    app = FastAPI(title="PULSE UI demo (not production)")
    app.state.ui_demo_mode = True
    app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32),
                       session_cookie="pulse_demo_session", same_site="lax", https_only=False)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    DemoBase.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    app.state.demo_session_factory = factory
    with factory() as db:
        now = datetime(2026, 10, 5, 9, 0)
        db.add_all([
            DemoChat(user_id=1, mode="q1", question="오늘 올릴 경제 숏폼 주제를 추천해 줘.", answer=ANSWERS["q1"], status="success", created_at=now),
            DemoChat(user_id=1, mode="q4", question="이 주제를 지금 올려도 괜찮을까?", answer=None, status="timeout", created_at=now - timedelta(minutes=10)),
            DemoChat(user_id=2, mode="q5", question="다른 사용자만 볼 수 있는 질문", answer="PRIVATE USER TWO", status="success", created_at=now + timedelta(minutes=10)),
        ])
        db.commit()

    def get_db():
        with factory() as db:
            yield db

    def require_login(request: Request) -> int:
        user_id = session_user_id(request)
        if user_id != 1:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
        return user_id

    install_ui(app, require_login=require_login, get_db=get_db, chat_model=DemoChat)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError):
        message = "질문은 1~500자로 입력하고 올바른 모드를 선택해 주세요." if request.url.path == "/api/chat" else "입력값을 확인해 주세요."
        return JSONResponse(status_code=422, content={"error": "INVALID_INPUT", "message": message})

    @app.post("/api/auth/login")
    def login(body: Credentials, request: Request):
        if body.email != "demo@example.com" or body.password != "demo-pass-2026":
            raise HTTPException(status_code=401, detail="미리보기 계정의 이메일과 비밀번호를 확인해 주세요.")
        request.session.clear()
        request.session["user_id"] = 1
        return {"message": "예시 계정으로 로그인했습니다."}

    @app.post("/api/auth/signup")
    def signup():
        return JSONResponse(status_code=503, content={"error": "DEMO_ONLY", "message": "미리보기에서는 회원가입을 제공하지 않습니다. A의 인증 API를 연결해 주세요."})

    @app.post("/api/auth/logout")
    def logout(request: Request, user_id: int = Depends(require_login)):
        request.session.clear()
        return {"message": "로그아웃했습니다."}

    @app.post("/api/chat")
    async def chat(body: ChatInput, user_id: int = Depends(require_login), db: Session = Depends(get_db)):
        logger.info("request_received user_id=%s path=/api/chat", user_id)
        logger.info("ai_call_start user_id=%s demo=true", user_id)
        await asyncio.sleep(0.35)
        status = "timeout" if body.message == "[timeout]" else "error" if body.message == "[error]" else "success"
        answer = ANSWERS[body.mode] if status == "success" else None
        logger.info("ai_call_%s user_id=%s demo=true", "success" if status == "success" else "fail", user_id)
        record = DemoChat(user_id=user_id, mode=body.mode, question=body.message, answer=answer, status=status, created_at=datetime.now())
        db.add(record)
        db.commit()
        db.refresh(record)
        logger.info("db_save_success user_id=%s chat_id=%s demo=true", user_id, record.id)
        if status != "success":
            return JSONResponse(status_code=504 if status == "timeout" else 502, content={
                "error": "AI_TIMEOUT" if status == "timeout" else "AI_ERROR",
                "message": "현재 응답이 지연되고 있어요. 잠시 후 다시 시도해 주세요." if status == "timeout" else "AI 응답에 실패했습니다. 잠시 후 다시 시도해 주세요.",
            })
        return {"chat_id": record.id, "answer": answer}

    return app


app = create_demo_app()
