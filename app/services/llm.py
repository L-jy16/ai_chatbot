"""A single server-side call to Codyssey's OpenAI-compatible chat endpoint."""

import httpx


class AITimeoutError(Exception):
    """The upstream service did not answer before the configured deadline."""


class AIServiceError(Exception):
    """The upstream service could not provide a usable answer."""


# Keep the name used by B's integration tests and call sites.
AIError = AIServiceError

# gpt-5-mini는 답변 전에 추론 토큰을 먼저 쓴다. 1200이면 추론에 다 써서 빈 답변이 온다.
# (실제 측정: 한도 1200 → content="", finish_reason=length / 한도 4000 → 1712토큰으로 정상 답변)
MAX_COMPLETION_TOKENS = 4000


async def ask_llm(system: str, messages: list[dict]) -> str:
    """Send one request. Never expose the provider key to the browser."""
    from app.config import settings

    key = settings.LLM_API_KEY.strip()
    if not key:
        raise AIServiceError("LLM_API_KEY is not configured")

    model = settings.LLM_MODEL.strip() or "gpt-5-mini"
    base_url = getattr(settings, "LLM_BASE_URL", "https://copa.codyssey.kr/v1").rstrip("/")
    try:
        timeout = float(settings.LLM_TIMEOUT_SECONDS)
        if timeout <= 0:
            raise ValueError
    except ValueError as exc:
        raise AIServiceError("LLM_TIMEOUT_SECONDS must be positive") from exc
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, *messages],
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json=payload,
            )
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise AITimeoutError from exc
    except httpx.HTTPError as exc:
        raise AIServiceError("AI request failed") from exc

    try:
        answer = response.json()["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise AIServiceError("AI response has an unexpected shape") from exc
    if not isinstance(answer, str) or not answer.strip():
        raise AIServiceError("AI response is empty")
    return answer.strip()
