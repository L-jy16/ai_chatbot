"""API 문서(Swagger UI·ReDoc·OpenAPI 명세)를 HTTP Basic 인증 뒤에 둔다.

DOCS_USERNAME과 DOCS_PASSWORD를 둘 다 설정했을 때만 문서 경로를 만들고, 아니면 404로 숨긴다.
HTTP로만 서비스하면 Basic 인증 값은 암호화되지 않으므로 다른 곳에 쓰지 않는 비밀번호를 쓴다.
FastAPI의 HTTPBasic은 인증 값을 ASCII로만 해석하므로 계정은 영문·숫자·기호로 정한다.
"""
import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials

OPENAPI_URL = "/openapi.json"


def install_docs(app: FastAPI, username: str, password: str) -> None:
    """계정이 있으면 /docs, /redoc, /openapi.json을 Basic 인증과 함께 등록한다."""
    if not username or not password:
        return

    basic = HTTPBasic()

    def require_docs_account(credentials: HTTPBasicCredentials = Depends(basic)) -> None:
        # 일치 여부를 응답 시간으로 추측하지 못하게 상수 시간 비교를 쓴다.
        user_ok = secrets.compare_digest(credentials.username.encode("utf-8"), username.encode("utf-8"))
        password_ok = secrets.compare_digest(credentials.password.encode("utf-8"), password.encode("utf-8"))
        if not (user_ok and password_ok):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Basic"})

    protected = [Depends(require_docs_account)]

    @app.get(OPENAPI_URL, include_in_schema=False, dependencies=protected)
    def openapi_spec() -> dict:
        return app.openapi()

    @app.get("/docs", include_in_schema=False, dependencies=protected)
    def swagger_ui():
        return get_swagger_ui_html(openapi_url=OPENAPI_URL, title=f"{app.title} - API 문서")

    @app.get("/redoc", include_in_schema=False, dependencies=protected)
    def redoc():
        return get_redoc_html(openapi_url=OPENAPI_URL, title=f"{app.title} - API 문서")
