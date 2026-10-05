import asyncio
import json

import httpx

from app.services.llm import ask_llm


def test_llm_sends_one_server_side_request(monkeypatch):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(200, json={"choices": [{"message": {"content": " 추천 답변 "}}]})

    transport = httpx.MockTransport(respond)
    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))
    monkeypatch.setenv("AI_API_KEY", "test-only")

    answer = asyncio.run(ask_llm("시스템", [{"role": "user", "content": "질문"}]))

    assert answer == "추천 답변"
    assert len(calls) == 1
    assert str(calls[0].url) == "https://copa.codyssey.kr/v1/chat/completions"
    body = json.loads(calls[0].content)
    assert body["model"] == "gpt-5-mini"
    assert [item["role"] for item in body["messages"]] == ["system", "user"]
    assert body["max_completion_tokens"] == 1200
