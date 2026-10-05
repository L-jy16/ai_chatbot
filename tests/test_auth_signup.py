import pytest
from sqlalchemy import select

from app.models import User
from app.security import verify_password


def test_signup_creates_user(signup):
    response = signup()
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "creator@example.com"
    assert isinstance(body["id"], int)


def test_signup_stores_bcrypt_hash_not_password(signup, db_session):
    signup()
    user = db_session.scalar(select(User).where(User.email == "creator@example.com"))
    assert user is not None
    assert user.password_hash != "shorts1234"
    assert verify_password("shorts1234", user.password_hash)


EMAIL_TAKEN = {"error": "EMAIL_TAKEN", "message": "이미 가입된 이메일이에요."}
INVALID_EMAIL = {"error": "INVALID_INPUT", "message": "올바른 이메일 형식이 아니에요."}
INVALID_PASSWORD = {
    "error": "INVALID_INPUT",
    "message": "비밀번호는 8자 이상, 72바이트 이하로 입력해 주세요.",
}


def test_signup_normalizes_email(signup):
    response = signup(email="  Creator@Example.COM ")
    assert response.status_code == 201
    assert response.json()["email"] == "creator@example.com"


def test_signup_rejects_duplicate_email(signup):
    signup()
    response = signup(email="CREATOR@example.com")
    assert response.status_code == 409
    assert response.json() == EMAIL_TAKEN


def test_signup_duplicate_race_returns_409(signup, monkeypatch):
    # 중복 확인을 통과한 뒤 다른 요청이 먼저 저장한 상황 → DB UNIQUE 제약 위반
    signup()
    monkeypatch.setattr("app.routers.auth.find_user_by_email", lambda db, email: None)
    response = signup()
    assert response.status_code == 409
    assert response.json() == EMAIL_TAKEN


@pytest.mark.parametrize("email", ["not-an-email", "a@b", "a@@b.com", ""])
def test_signup_rejects_invalid_email(signup, email):
    response = signup(email=email)
    assert response.status_code == 422
    assert response.json() == INVALID_EMAIL


@pytest.mark.parametrize("password", ["short12", "가" * 25])  # 7자, 75바이트
def test_signup_rejects_bad_password_length(signup, password):
    response = signup(password=password)
    assert response.status_code == 422
    assert response.json() == INVALID_PASSWORD


@pytest.mark.parametrize("password", ["a" * 8, "a" * 72, "가나다라마바사아"])  # 경계값, 한글 8자(24바이트)
def test_signup_accepts_password_within_limits(signup, password):
    assert signup(password=password).status_code == 201


def post_json_text(client, path, raw):
    # 브라우저 JSON.stringify처럼 짝 없는 서로게이트를 \ud800 이스케이프로 보낸다.
    return client.post(path, content=raw, headers={"content-type": "application/json"})


def test_signup_rejects_unpaired_surrogate_in_password(client):
    raw = b'{"email": "creator@example.com", "password": "abcdefgh\\ud800"}'
    response = post_json_text(client, "/api/auth/signup", raw)
    assert response.status_code == 422
    assert response.json() == INVALID_PASSWORD


def test_signup_rejects_unpaired_surrogate_in_email(client):
    raw = b'{"email": "a\\ud800@example.com", "password": "shorts1234"}'
    response = post_json_text(client, "/api/auth/signup", raw)
    assert response.status_code == 422
    assert response.json() == INVALID_EMAIL


CAFE_NFC = "café@example.com"  # é를 한 글자로 쓴 형태
CAFE_NFD = "café@example.com"  # e + 결합 악센트 두 글자로 쓴 형태 (macOS 입력 등)


def test_signup_treats_nfc_and_nfd_email_as_same_account(signup):
    assert signup(email=CAFE_NFC).status_code == 201
    response = signup(email=CAFE_NFD)
    assert response.status_code == 409
    assert response.json() == EMAIL_TAKEN


def test_signup_normalizes_fullwidth_email(signup):
    response = signup(email="fw@ｅｘａｍｐｌｅ.com")  # 전각 example
    assert response.status_code == 201
    assert response.json()["email"] == "fw@example.com"
