"""운영자 화면(API 문서, DB 조회)을 HTTP Basic 인증으로 막는 공통 의존성.

HTTP로만 서비스하면 Basic 인증 값은 암호화되지 않으므로 다른 곳에 쓰지 않는 비밀번호를 쓴다.
FastAPI의 HTTPBasic은 인증 값을 ASCII로만 해석하므로 계정은 영문·숫자·기호로 정한다.
"""
import secrets
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials


def basic_auth_guard(username: str, password: str) -> Callable | None:
    """계정이 둘 다 있으면 Basic 인증 의존성을, 아니면 None(그 화면을 만들지 않음)을 돌려준다."""
    if not username or not password:
        return None

    basic = HTTPBasic()

    def require_account(credentials: HTTPBasicCredentials = Depends(basic)) -> None:
        # 일치 여부를 응답 시간으로 추측하지 못하게 상수 시간 비교를 쓴다.
        user_ok = secrets.compare_digest(credentials.username.encode("utf-8"), username.encode("utf-8"))
        password_ok = secrets.compare_digest(credentials.password.encode("utf-8"), password.encode("utf-8"))
        if not (user_ok and password_ok):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Basic"})

    return require_account
