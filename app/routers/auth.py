import logging

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import hash_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class SignupRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, db: Session = Depends(get_db)) -> UserResponse:
    user = User(email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("signup_success user_id=%s", user.id)
    return UserResponse(id=user.id, email=user.email)
