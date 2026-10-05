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
