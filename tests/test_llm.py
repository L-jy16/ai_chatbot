import asyncio
import json
import sys
import types
from types import SimpleNamespace

import httpx
import pytest

from app.services.llm import AIServiceError, AITimeoutError, ask_llm


@pytest.fixture(autouse=True)
def config_settings(monkeypatch):
    """A's settings contract, supplied only inside the test."""
    module = types.ModuleType("app.config")
    module.settings = SimpleNamespace(
        LLM_API_KEY="test-only", LLM_MODEL="", LLM_TIMEOUT_SECONDS=30
    )
    monkeypatch.setitem(sys.modules, "app.config", module)
    return module.settings


def test_llm_sends_one_server_side_request(monkeypatch):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(200, json={"choices": [{"message": {"content": " 추천 답변 "}}]})

    transport = httpx.MockTransport(respond)
    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))

    answer = asyncio.run(ask_llm("시스템", [{"role": "user", "content": "질문"}]))

    assert answer == "추천 답변"
    assert len(calls) == 1
    assert str(calls[0].url) == "https://copa.codyssey.kr/v1/chat/completions"
    body = json.loads(calls[0].content)
    assert body["model"] == "gpt-5-mini"
    assert [item["role"] for item in body["messages"]] == ["system", "user"]
    assert body["max_completion_tokens"] == 1200


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        (httpx.Response(429), "AI request failed"),
        (httpx.Response(200, json={"choices": []}), "unexpected shape"),
        (httpx.Response(200, json={"choices": [{"message": {"content": ""}}]}), "empty"),
    ],
)
def test_llm_failure_is_normalized_without_retry(monkeypatch, response, expected):
    calls = []

    def respond(request):
        calls.append(request)
        return response

    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=httpx.MockTransport(respond), **kwargs))

    with pytest.raises(AIServiceError, match=expected):
        asyncio.run(ask_llm("system", [{"role": "user", "content": "question"}]))
    assert len(calls) == 1


def test_llm_timeout_has_dedicated_error(monkeypatch):
    def respond(request):
        raise httpx.ReadTimeout("slow", request=request)

    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=httpx.MockTransport(respond), **kwargs))

    with pytest.raises(AITimeoutError):
        asyncio.run(ask_llm("system", [{"role": "user", "content": "question"}]))


def test_llm_does_not_call_api_without_key(config_settings):
    config_settings.LLM_API_KEY = ""
    with pytest.raises(AIServiceError, match="not configured"):
        asyncio.run(ask_llm("system", []))
