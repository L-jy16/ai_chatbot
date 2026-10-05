from fastapi import Depends, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import APIError
from app.models import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """세션의 로그인 사용자를 돌려준다. 로그인하지 않았으면 None.

    화면 라우트는 이 함수를 받아 None이면 /login으로 리다이렉트한다.
    """
    user_id = request.session.get("user_id")
    if user_id is None:
        return None

    user = db.get(User, user_id)
    if user is None:
        # 삭제된 사용자의 세션은 비운다.
        request.session.clear()
    return user


def require_login(user: User | None = Depends(get_current_user)) -> User:
    """로그인한 사용자만 통과시킨다. API 라우트에서 Depends(require_login)으로 쓴다."""
    if user is None:
        raise APIError(status.HTTP_401_UNAUTHORIZED, "LOGIN_REQUIRED", "로그인이 필요해요.")
    return user
