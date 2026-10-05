import logging

from sqlalchemy import select

from app.models import User

LOGIN_REQUIRED = {"error": "LOGIN_REQUIRED", "message": "로그인이 필요해요."}


def test_signup_does_not_log_in(signup, client):
    signup()
    assert client.post("/api/auth/logout").status_code == 401


def test_session_of_deleted_user_is_treated_as_logged_out(logged_in_client, db_session):
    user = db_session.scalar(select(User).where(User.email == "creator@example.com"))
    db_session.delete(user)
    db_session.commit()

    response = logged_in_client.post("/api/auth/logout")
    assert response.status_code == 401
    assert response.json() == LOGIN_REQUIRED


def test_tampered_session_cookie_is_treated_as_logged_out(client):
    client.cookies.set("session", "tampered-value")
    response = client.post("/api/auth/logout")
    assert response.status_code == 401
    assert response.json() == LOGIN_REQUIRED


def test_session_cookie_is_httponly_and_samesite_lax(signup, login):
    signup()
    set_cookie = login().headers["set-cookie"].lower()
    assert "httponly" in set_cookie
    assert "samesite=lax" in set_cookie


def test_auth_events_are_logged(signup, login, client, caplog):
    caplog.set_level(logging.INFO, logger="app.routers.auth")
    signup()
    signup()
    login(password="wrong-password")
    login()
    client.post("/api/auth/logout")

    # HTTP 클라이언트 로그의 URL(/api/auth/logout)에 속지 않도록 auth 로거의 기록만 본다.
    messages = [record.getMessage() for record in caplog.records if record.name == "app.routers.auth"]
    for event in ["signup_success", "signup_duplicate", "login_failed", "login_success", "logout"]:
        assert any(message.startswith(event + " ") for message in messages), event


def test_passwords_never_appear_in_logs(signup, login, caplog):
    caplog.set_level(logging.INFO)
    signup(password="secret-pass-123")
    login(password="secret-pass-123")
    login(password="wrong-pass-456")

    assert "secret-pass-123" not in caplog.text
    assert "wrong-pass-456" not in caplog.text
    assert "$2b$" not in caplog.text


def test_deleted_users_session_does_not_become_next_signup(logged_in_client, signup, db_session):
    user = db_session.scalar(select(User).where(User.email == "creator@example.com"))
    db_session.delete(user)
    db_session.commit()

    # SQLite가 지운 id를 새 가입자에게 재사용하면, 옛 쿠키가 그 사람으로 로그인된다.
    signup(email="newcomer@example.com")

    response = logged_in_client.post("/api/auth/logout")
    assert response.status_code == 401
    assert response.json() == LOGIN_REQUIRED
