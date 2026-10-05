"""Exercise C's route against a tiny test-only version of A's contract."""

import importlib
import sys
import types
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, Header, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import Integer, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError

from app.routers.chat import create_router
from app.errors import register_error_handlers
from app.services import llm
from app.services.scenarios import q5, q6


@pytest.fixture
def chat_app(monkeypatch):
    class Base(DeclarativeBase):
        pass

    class User(Base):
        __tablename__ = "users"
        id: Mapped[int] = mapped_column(Integer, primary_key=True)

    database_module = types.ModuleType("app.database")
    database_module.Base = Base
    monkeypatch.setitem(sys.modules, "app.database", database_module)
    sys.modules.pop("app.models.chat", None)
    chat_module = importlib.import_module("app.models.chat")
    Chat = chat_module.Chat

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as db:
        db.add_all([User(id=1), User(id=2)])
        db.commit()

    def get_db():
        with Session() as db:
            yield db

    def require_login(x_test_user=Header(default=None)):
        if x_test_user is None:
            raise HTTPException(status_code=401)
        return SimpleNamespace(id=int(x_test_user))

    class Calls(list):
        failure = None

    calls = Calls()

    async def fake_llm(system, messages):
        calls.append((system, messages))
        if calls.failure:
            raise calls.failure
        return "추천 답변"

    async def fake_prompt(message):
        return f"Q5 근거와 형식: {message}"

    monkeypatch.setattr(llm, "ask_llm", fake_llm)
    monkeypatch.setattr(q5, "build_prompt", fake_prompt)
    monkeypatch.setattr(q6, "build_prompt", fake_prompt)
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(create_router(require_login, get_db))
    yield TestClient(app), Session, Chat, calls
    sys.modules.pop("app.models.chat", None)
    engine.dispose()


def test_chat_saves_answer_for_authenticated_user(chat_app):
    client, Session, Chat, calls = chat_app
    response = client.post(
        "/api/chat", json={"mode": "q5", "message": "  금리 주제  "}, headers={"X-Test-User": "1"}
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "추천 답변"
    assert len(calls) == 1
    assert calls[0][1][-1] == {"role": "user", "content": "금리 주제"}
    with Session() as db:
        row = db.get(Chat, response.json()["chat_id"])
        assert (row.user_id, row.mode, row.question, row.answer, row.status) == (
            1, "q5", "금리 주제", "추천 답변", "success"
        )
        assert row.created_at is not None


def _labelled_prompt(label):
    async def build_prompt(message, *args, **kwargs):
        return label

    return build_prompt


@pytest.mark.parametrize(
    ("mode", "expected_system"),
    [
        ("q1", "B 오늘의 주제"),
        ("q2", "B 운영 채널 추천"),
        ("q3", "B 타이밍 체크"),
        ("q4", "C 새로운 각도"),
        ("q5", "C 다음 편 기획"),
    ],
)
def test_screen_modes_route_to_owner_scenarios(chat_app, monkeypatch, mode, expected_system):
    # 화면(D)의 Q1~Q5 번호와 시나리오 파일 번호가 달라서 라우터가 대응시킨다.
    from app.services.scenarios import q1, q2, q3

    monkeypatch.setattr(q1, "build_prompt", _labelled_prompt("B 오늘의 주제"))
    monkeypatch.setattr(q2, "build_prompt", _labelled_prompt("B 운영 채널 추천"))
    monkeypatch.setattr(q3, "build_prompt", _labelled_prompt("B 타이밍 체크"))
    monkeypatch.setattr(q5, "build_prompt", _labelled_prompt("C 새로운 각도"))
    monkeypatch.setattr(q6, "build_prompt", _labelled_prompt("C 다음 편 기획"))
    client, _, _, calls = chat_app

    response = client.post("/api/chat", json={"mode": mode, "message": "질문"}, headers={"X-Test-User": "1"})

    assert response.status_code == 200
    assert calls[0][0] == expected_system


def test_timing_check_passes_analysis_keyword(chat_app, monkeypatch):
    from app.services.scenarios import q3

    seen = {}

    async def timing_prompt(message, keyword=None):
        seen["keyword"] = keyword
        return "B 타이밍 체크"

    monkeypatch.setattr(q3, "build_prompt", timing_prompt)
    client, _, _, _ = chat_app
    response = client.post(
        "/api/chat", json={"mode": "q3", "message": "지금 올려도 돼?", "keyword": "금리 인하"},
        headers={"X-Test-User": "1"},
    )
    assert response.status_code == 200
    assert seen["keyword"] == "금리 인하"


def test_channel_mode_reuses_previous_questions_as_context(chat_app, monkeypatch):
    from app.services.scenarios import q2

    seen = {}

    async def channel_prompt(message, context=None):
        seen["context"] = context
        return "B 운영 채널 추천"

    monkeypatch.setattr(q2, "build_prompt", channel_prompt)
    client, Session, Chat, _ = chat_app
    earlier = "최근 업로드 주제: 환율 상승\n질문: 오늘 뭐 올릴까?"
    with Session() as db:
        db.add(Chat(user_id=1, mode="q2", question=earlier, answer="답", status="success"))
        db.commit()

    response = client.post("/api/chat", json={"mode": "q2", "message": "이어서 추천해 줘"}, headers={"X-Test-User": "1"})

    assert response.status_code == 200
    assert seen["context"] == [earlier]


def test_login_and_invalid_input_stop_before_ai(chat_app):
    client, Session, Chat, calls = chat_app
    assert client.post("/api/chat", json={"mode": "q5", "message": "질문"}).status_code == 401
    response = client.post(
        "/api/chat", json={"mode": "q5", "message": "  "}, headers={"X-Test-User": "1"}
    )
    assert response.status_code == 422
    assert response.json()["error"] == "INVALID_INPUT"
    assert calls == []
    with Session() as db:
        assert db.query(Chat).count() == 0


def test_context_is_limited_to_current_user(chat_app):
    client, Session, Chat, calls = chat_app
    with Session() as db:
        db.add(Chat(user_id=2, mode="q5", question="다른 사람 질문", answer="비밀", status="success"))
        for index in range(6):
            db.add(Chat(user_id=1, mode="q5", question=f"질문 {index}", answer=f"답 {index}", status="success"))
        db.add(Chat(user_id=1, mode="q5", question="실패", answer=None, status="timeout"))
        db.commit()

    response = client.post(
        "/api/chat", json={"mode": "q5", "message": "다음은?"}, headers={"X-Test-User": "1"}
    )
    assert response.status_code == 200
    messages = calls[0][1]
    assert len(messages) == 11
    assert messages[0]["content"] == "질문 1"
    assert messages[-1]["content"] == "다음은?"
    assert all("다른 사람" not in item["content"] for item in messages)


@pytest.mark.parametrize(
    ("failure", "code", "saved_status", "http_status"),
    [
        (llm.AITimeoutError(), "AI_TIMEOUT", "timeout", 504),
        (llm.AIServiceError(), "AI_ERROR", "error", 502),
    ],
)
def test_ai_failure_is_saved_without_answer(chat_app, failure, code, saved_status, http_status):
    client, Session, Chat, calls = chat_app
    calls.failure = failure

    response = client.post(
        "/api/chat", json={"mode": "q5", "message": "다음 편"}, headers={"X-Test-User": "1"}
    )

    assert response.status_code == http_status
    assert response.json()["error"] == code
    with Session() as db:
        row = db.query(Chat).one()
        assert (row.status, row.answer) == (saved_status, None)


def test_db_failure_never_returns_success(chat_app, monkeypatch):
    client, Session, Chat, calls = chat_app
    original_commit = Session.class_.commit

    def fail_commit(self):
        raise SQLAlchemyError("simulated DB write failure")

    with monkeypatch.context() as patch:
        patch.setattr(Session.class_, "commit", fail_commit)
        response = client.post(
            "/api/chat", json={"mode": "q5", "message": "질문"}, headers={"X-Test-User": "1"}
        )

    assert response.status_code == 500
    assert response.json()["error"] == "DB_ERROR"
    with Session() as db:
        assert db.query(Chat).count() == 0

    assert Session.class_.commit is original_commit
    next_response = client.post(
        "/api/chat", json={"mode": "q5", "message": "다음 질문"}, headers={"X-Test-User": "1"}
    )
    assert next_response.status_code == 200


def test_ai_failure_log_keeps_reason_for_tracing(chat_app, caplog):
    # 로그만 보고 원인을 추적할 수 있어야 한다. 사유는 우리 코드가 정한 문구이며 키·원본 응답은 넣지 않는다.
    client, _, _, calls = chat_app
    calls.failure = llm.AIServiceError("AI response is empty")
    caplog.set_level("WARNING", logger="app.routers.chat")

    client.post("/api/chat", json={"mode": "q4", "message": "질문"}, headers={"X-Test-User": "1"})

    assert any("ai_call_fail" in m and "detail=AI response is empty" in m for m in caplog.messages)
