"""A single server-side call to Codyssey's OpenAI-compatible chat endpoint."""

import os

import httpx


class AITimeoutError(Exception):
    """The upstream service did not answer before the configured deadline."""


class AIServiceError(Exception):
    """The upstream service could not provide a usable answer."""


async def ask_llm(system: str, messages: list[dict]) -> str:
    """Send one request. Never expose the provider key to the browser."""
    key = os.getenv("AI_API_KEY")
    if not key:
        raise AIServiceError("AI_API_KEY is not configured")

    base_url = os.getenv("AI_BASE_URL", "https://copa.codyssey.kr/v1").rstrip("/")
    model = os.getenv("AI_MODEL", "gpt-5-mini")
    try:
        timeout = float(os.getenv("AI_TIMEOUT_SECONDS", "30"))
        if timeout <= 0:
            raise ValueError
    except ValueError as exc:
        raise AIServiceError("AI_TIMEOUT_SECONDS must be positive") from exc
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, *messages],
        "max_completion_tokens": 1200,
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
