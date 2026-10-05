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

from app.routers.chat import create_router
from app.services import llm
from app.services.scenarios import q5


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

    calls = []

    async def fake_llm(system, messages):
        calls.append((system, messages))
        return "추천 답변"

    async def fake_prompt(message):
        return f"Q5 근거와 형식: {message}"

    monkeypatch.setattr(llm, "ask_llm", fake_llm)
    monkeypatch.setattr(q5, "build_prompt", fake_prompt)
    app = FastAPI()
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
