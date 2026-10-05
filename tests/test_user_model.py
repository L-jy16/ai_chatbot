import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app.database import create_db_engine
from app.main import app
from app.models import User


def test_user_gets_id_and_created_at(db_session):
    user = User(email="creator@example.com", password_hash="x" * 60)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.created_at is not None


def test_duplicate_email_is_rejected_by_db(db_session):
    db_session.add(User(email="creator@example.com", password_hash="x" * 60))
    db_session.commit()

    db_session.add(User(email="creator@example.com", password_hash="y" * 60))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_app_startup_creates_users_table(tmp_path, monkeypatch):
    startup_engine = create_db_engine(f"sqlite:///{tmp_path / 'startup.db'}")
    monkeypatch.setattr("app.main.engine", startup_engine)

    with TestClient(app):  # with 블록이어야 lifespan(create_all)이 실행된다
        pass

    assert inspect(startup_engine).has_table("users")
    startup_engine.dispose()
