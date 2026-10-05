from types import SimpleNamespace

import pytest

from app.dependencies import get_current_user, require_login
from app.errors import APIError
from app.models import User


def make_request(session=None):
    # get_current_user는 request.session만 쓰므로 가짜 요청 객체로 충분하다.
    return SimpleNamespace(session={} if session is None else session)


def add_user(db_session, email="creator@example.com"):
    user = User(email=email, password_hash="x" * 60)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_get_current_user_without_session_returns_none(db_session):
    assert get_current_user(make_request(), db_session) is None


def test_get_current_user_returns_logged_in_user(db_session):
    user = add_user(db_session)
    current = get_current_user(make_request({"user_id": user.id}), db_session)
    assert current is not None
    assert current.id == user.id


def test_get_current_user_clears_session_of_missing_user(db_session):
    request = make_request({"user_id": 999})
    assert get_current_user(request, db_session) is None
    assert request.session == {}


def test_require_login_rejects_anonymous():
    with pytest.raises(APIError) as exc_info:
        require_login(None)
    assert exc_info.value.status_code == 401
    assert exc_info.value.error == "LOGIN_REQUIRED"
    assert exc_info.value.message == "로그인이 필요해요."


def test_require_login_passes_user_through(db_session):
    user = add_user(db_session)
    assert require_login(user) is user
