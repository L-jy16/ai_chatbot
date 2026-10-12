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
    assert body["max_completion_tokens"] == 4000


def test_llm_leaves_room_for_reasoning_tokens(monkeypatch):
    # gpt-5-mini는 답변을 쓰기 전에 추론 토큰을 먼저 쓴다. 실제 API에서 한도 1200이면
    # 추론에 다 써서 content=""·finish_reason=length가 왔고, 4000이면 1712토큰으로 정상 답변했다.
    reasoning_tokens, answer_tokens = 1700, 300

    def respond(request):
        budget = json.loads(request.content)["max_completion_tokens"]
        if budget < reasoning_tokens + answer_tokens:
            choice = {"message": {"content": ""}, "finish_reason": "length"}
        else:
            choice = {"message": {"content": "추천 답변"}, "finish_reason": "stop"}
        return httpx.Response(200, json={"choices": [choice]})

    transport = httpx.MockTransport(respond)
    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))

    assert asyncio.run(ask_llm("시스템", [{"role": "user", "content": "질문"}])) == "추천 답변"


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
