import logging

from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_login
from app.errors import DEFAULT_INVALID_INPUT_MESSAGE, APIError
from app.models import User
from app.security import MAX_PASSWORD_BYTES, hash_password, verify_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

PASSWORD_MIN_LENGTH = 8
INVALID_EMAIL_MESSAGE = "올바른 이메일 형식이 아니에요."
INVALID_PASSWORD_MESSAGE = "비밀번호는 8자 이상, 72바이트 이하로 입력해 주세요."


def normalize_email(value: str) -> str:
    """대소문자·앞뒤 공백이 달라도 같은 계정으로 보도록 이메일을 정규화한다."""
    return value.strip().lower()


def ensure_utf8(value: str, message: str) -> str:
    """짝 없는 서로게이트처럼 UTF-8로 바꿀 수 없는 문자가 있으면 message로 거절한다."""
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        raise ValueError(message) from None
    return value


class SignupRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, value: str) -> str:
        email = normalize_email(ensure_utf8(value, INVALID_EMAIL_MESSAGE))
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            raise ValueError(INVALID_EMAIL_MESSAGE) from None
        return email

    @field_validator("password")
    @classmethod
    def password_length_must_fit(cls, value: str) -> str:
        ensure_utf8(value, INVALID_PASSWORD_MESSAGE)
        too_short = len(value) < PASSWORD_MIN_LENGTH
        too_long = len(value.encode("utf-8")) > MAX_PASSWORD_BYTES
        if too_short or too_long:
            raise ValueError(INVALID_PASSWORD_MESSAGE)
        return value


LOGIN_BLANK_MESSAGE = "이메일과 비밀번호를 입력해 주세요."


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_not_blank(cls, value: str) -> str:
        email = normalize_email(ensure_utf8(value, DEFAULT_INVALID_INPUT_MESSAGE))
        if not email:
            raise ValueError(LOGIN_BLANK_MESSAGE)
        return email

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, value: str) -> str:
        if not value:
            raise ValueError(LOGIN_BLANK_MESSAGE)
        return ensure_utf8(value, DEFAULT_INVALID_INPUT_MESSAGE)


class UserResponse(BaseModel):
    id: int
    email: str


def email_for_log(email: str) -> str:
    """로그에 남길 이메일. 형식이 올바른 이메일만 그대로 남긴다.

    이메일 칸에 비밀번호를 잘못 넣은 경우, 줄바꿈으로 로그 줄을 위조하려는 경우,
    지나치게 긴 입력은 값 대신 <invalid>로 남긴다.
    """
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return "<invalid>"
    return email


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


@router.post("/login")
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)) -> UserResponse:
    user = find_user_by_email(db, body.email)
    if user is None or not verify_password(body.password, user.password_hash):
        logger.warning("login_failed email=%s", email_for_log(body.email))
        raise APIError(
            status.HTTP_401_UNAUTHORIZED,
            "INVALID_CREDENTIALS",
            "이메일 또는 비밀번호가 올바르지 않아요.",
        )

    request.session.clear()
    request.session["user_id"] = user.id
    logger.info("login_success user_id=%s", user.id)
    return UserResponse(id=user.id, email=user.email)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, user: User = Depends(require_login)) -> None:
    request.session.clear()
    logger.info("logout user_id=%s", user.id)
