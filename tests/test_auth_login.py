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


@pytest.mark.parametrize(
    "raw",
    [
        b'{"email": "creator@example.com", "password": "abcdefgh\\ud800"}',
        b'{"email": "a\\ud800@example.com", "password": "shorts1234"}',
    ],
)
def test_login_rejects_unpaired_surrogate_without_500(signup, client, raw):
    # 브라우저 JSON.stringify처럼 짝 없는 서로게이트를 \ud800 이스케이프로 보낸다.
    signup()
    response = client.post("/api/auth/login", content=raw, headers={"content-type": "application/json"})
    assert response.status_code == 422
    assert response.json() == {"error": "INVALID_INPUT", "message": "입력값이 올바르지 않아요."}


def test_login_matches_email_written_in_other_unicode_form(signup, login):
    signup(email="café@example.com")  # é 한 글자
    assert login(email="café@example.com").status_code == 200  # e + 결합 악센트
