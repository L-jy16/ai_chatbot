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


def auth_log_messages(caplog):
    return [record.getMessage() for record in caplog.records if record.name == "app.routers.auth"]


def test_login_failed_log_cannot_be_forged_with_newline(login, caplog):
    caplog.set_level(logging.INFO)
    login(email="x\n2026-10-05 12:00:00 INFO app.routers.auth: login_success user_id=1")

    messages = auth_log_messages(caplog)
    assert not any("\n" in message for message in messages)
    assert not any(message.startswith("login_success") for message in messages)


def test_password_typed_into_email_field_is_not_logged(login, caplog):
    caplog.set_level(logging.INFO)
    login(email="secret-pass-123")
    assert "secret-pass-123" not in caplog.text


def test_login_failed_log_is_length_capped(login, caplog):
    caplog.set_level(logging.INFO)
    login(email="a" * 5000 + "@example.com")
    assert all(len(message) < 300 for message in auth_log_messages(caplog))


def test_login_failed_log_keeps_valid_email(login, caplog):
    caplog.set_level(logging.INFO)
    login(email="nobody@example.com")
    assert "login_failed email=nobody@example.com" in auth_log_messages(caplog)
