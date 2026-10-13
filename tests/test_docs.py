import base64

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.docs import install_docs

DOC_PATHS = ["/docs", "/redoc", "/openapi.json"]


def basic(username, password):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def make_client(username, password):
    app = FastAPI(title="docs test", docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/api/ping")
    def ping():
        return {"ok": True}

    install_docs(app, username, password)
    return TestClient(app)


@pytest.mark.parametrize("path", DOC_PATHS)
def test_main_app_hides_docs_without_account(client, path):
    # 문서 계정을 설정하지 않은 서버는 API 목록과 스키마를 공개하지 않는다.
    assert client.get(path).status_code == 404


@pytest.mark.parametrize("username,password", [("", ""), ("admin", ""), ("", "secret-pass")])
def test_docs_stay_hidden_unless_both_values_are_set(username, password):
    client = make_client(username, password)
    for path in DOC_PATHS:
        assert client.get(path, headers=basic("admin", "secret-pass")).status_code == 404


@pytest.mark.parametrize("path", DOC_PATHS)
def test_docs_ask_for_basic_auth(path):
    response = make_client("admin", "secret-pass").get(path)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"


@pytest.mark.parametrize("username,password", [("admin", "wrong"), ("other", "secret-pass"), ("admin", "")])
def test_docs_reject_wrong_account(username, password):
    client = make_client("admin", "secret-pass")
    for path in DOC_PATHS:
        response = client.get(path, headers=basic(username, password))
        assert response.status_code == 401


def test_docs_open_with_right_account():
    client = make_client("admin", "S3cret-pass!")
    headers = basic("admin", "S3cret-pass!")
    swagger = client.get("/docs", headers=headers)
    assert swagger.status_code == 200 and "/openapi.json" in swagger.text
    assert client.get("/redoc", headers=headers).status_code == 200
    spec = client.get("/openapi.json", headers=headers)
    assert spec.status_code == 200
    assert "/api/ping" in spec.json()["paths"]
    # 문서 주소 자체는 명세에 넣지 않는다.
    assert not set(DOC_PATHS) & set(spec.json()["paths"])
