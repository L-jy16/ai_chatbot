import pytest

INVALID_CREDENTIALS = {
    "error": "INVALID_CREDENTIALS",
    "message": "이메일 또는 비밀번호가 올바르지 않아요.",
}
BLANK_INPUT = {"error": "INVALID_INPUT", "message": "이메일과 비밀번호를 입력해 주세요."}


def test_login_sets_session_cookie(signup, login, client):
    signup()
    response = login()
    assert response.status_code == 200
    assert response.json()["email"] == "creator@example.com"
    assert "session" in client.cookies


def test_login_with_wrong_password_fails(signup, login, client):
    signup()
    response = login(password="wrong-password")
    assert response.status_code == 401
    assert response.json() == INVALID_CREDENTIALS
    assert "session" not in client.cookies


def test_login_with_unknown_email_gets_same_message(login):
    response = login(email="nobody@example.com")
    assert response.status_code == 401
    assert response.json() == INVALID_CREDENTIALS


def test_login_email_ignores_case_and_spaces(signup, login):
    signup()
    assert login(email="  CREATOR@Example.com ").status_code == 200


def test_login_with_over_72_byte_password_is_401_not_500(signup, login):
    signup()
    response = login(password="a" * 73)
    assert response.status_code == 401
    assert response.json() == INVALID_CREDENTIALS


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "", "password": "shorts1234"},
        {"email": "   ", "password": "shorts1234"},
        {"email": "creator@example.com", "password": ""},
    ],
)
def test_login_rejects_blank_fields(client, payload):
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 422
    assert response.json() == BLANK_INPUT
