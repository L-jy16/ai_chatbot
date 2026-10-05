from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, field_validator

from app.errors import APIError, register_error_handlers


class EchoRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("내용을 입력해 주세요.")
        return value


def make_client() -> TestClient:
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/boom")
    def boom():
        raise APIError(504, "AI_TIMEOUT", "현재 응답이 지연되고 있어요.")

    @app.post("/echo")
    def echo(body: EchoRequest):
        return {"text": body.text}

    return TestClient(app)


def test_api_error_uses_common_shape():
    response = make_client().get("/boom")
    assert response.status_code == 504
    assert response.json() == {"error": "AI_TIMEOUT", "message": "현재 응답이 지연되고 있어요."}


def test_value_error_message_becomes_invalid_input_message():
    response = make_client().post("/echo", json={"text": "   "})
    assert response.status_code == 422
    assert response.json() == {"error": "INVALID_INPUT", "message": "내용을 입력해 주세요."}


def test_missing_field_gets_default_message():
    response = make_client().post("/echo", json={})
    assert response.status_code == 422
    assert response.json() == {"error": "INVALID_INPUT", "message": "입력값이 올바르지 않아요."}


def test_malformed_json_gets_default_message():
    response = make_client().post(
        "/echo", content=b"{not json", headers={"content-type": "application/json"}
    )
    assert response.status_code == 422
    assert response.json() == {"error": "INVALID_INPUT", "message": "입력값이 올바르지 않아요."}


def test_non_object_body_gets_default_message():
    response = make_client().post("/echo", json=["text"])
    assert response.status_code == 422
    assert response.json() == {"error": "INVALID_INPUT", "message": "입력값이 올바르지 않아요."}
