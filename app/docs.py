"""API 문서(Swagger UI·ReDoc·OpenAPI 명세)를 HTTP Basic 인증 뒤에 둔다.

DOCS_USERNAME과 DOCS_PASSWORD를 둘 다 설정했을 때만 문서 경로를 만들고, 아니면 404로 숨긴다.
"""
from fastapi import Depends, FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

from app.basic_auth import basic_auth_guard

OPENAPI_URL = "/openapi.json"


def install_docs(app: FastAPI, username: str, password: str) -> None:
    """계정이 있으면 /docs, /redoc, /openapi.json을 Basic 인증과 함께 등록한다."""
    guard = basic_auth_guard(username, password)
    if guard is None:
        return

    protected = [Depends(guard)]

    @app.get(OPENAPI_URL, include_in_schema=False, dependencies=protected)
    def openapi_spec() -> dict:
        return app.openapi()

    @app.get("/docs", include_in_schema=False, dependencies=protected)
    def swagger_ui():
        return get_swagger_ui_html(openapi_url=OPENAPI_URL, title=f"{app.title} - API 문서")

    @app.get("/redoc", include_in_schema=False, dependencies=protected)
    def redoc():
        return get_redoc_html(openapi_url=OPENAPI_URL, title=f"{app.title} - API 문서")
