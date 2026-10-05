import logging

from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import APIError
from app.models import User
from app.security import MAX_PASSWORD_BYTES, hash_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

PASSWORD_MIN_LENGTH = 8


def normalize_email(value: str) -> str:
    """대소문자·앞뒤 공백이 달라도 같은 계정으로 보도록 이메일을 정규화한다."""
    return value.strip().lower()


class SignupRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, value: str) -> str:
        email = normalize_email(value)
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            raise ValueError("올바른 이메일 형식이 아니에요.") from None
        return email

    @field_validator("password")
    @classmethod
    def password_length_must_fit(cls, value: str) -> str:
        too_short = len(value) < PASSWORD_MIN_LENGTH
        too_long = len(value.encode("utf-8")) > MAX_PASSWORD_BYTES
        if too_short or too_long:
            raise ValueError("비밀번호는 8자 이상, 72바이트 이하로 입력해 주세요.")
        return value


class UserResponse(BaseModel):
    id: int
    email: str


def find_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def email_taken(email: str) -> APIError:
    logger.info("signup_duplicate email=%s", email)
    return APIError(status.HTTP_409_CONFLICT, "EMAIL_TAKEN", "이미 가입된 이메일이에요.")


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, db: Session = Depends(get_db)) -> UserResponse:
    if find_user_by_email(db, body.email) is not None:
        raise email_taken(body.email)

    user = User(email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # 중복 확인과 저장 사이에 같은 이메일이 먼저 가입된 경우
        db.rollback()
        raise email_taken(body.email) from None
    db.refresh(user)
    logger.info("signup_success user_id=%s", user.id)
    return UserResponse(id=user.id, email=user.email)
