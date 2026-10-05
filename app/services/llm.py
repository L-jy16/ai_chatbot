"""OpenAI Chat Completions 호환 게이트웨이. 키와 원본 오류 본문은 기록하지 않는다."""
import asyncio
import logging

import httpx2 as httpx

from app.config import settings

logger = logging.getLogger(__name__)


class AITimeoutError(Exception):
    pass


class AIError(Exception):
    pass


async def ask_llm(system: str, messages: list[dict]) -> str:
    if not settings.LLM_API_KEY or not settings.LLM_MODEL:
        raise AIError("LLM 설정이 필요합니다.")

    async def request() -> str:
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            response = await client.post(
                settings.LLM_BASE_URL.rstrip("/") + "/chat/completions",
                headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
                json={
                    "model": settings.LLM_MODEL,
                    "messages": [{"role": "system", "content": system}, *messages],
                },
            )
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"]
            if not isinstance(answer, str) or not answer.strip():
                raise AIError("AI 응답이 비어 있습니다.")
            return answer.strip()

    try:
        return await asyncio.wait_for(request(), timeout=settings.LLM_TIMEOUT_SECONDS)
    except (asyncio.TimeoutError, httpx.TimeoutException) as exc:
        raise AITimeoutError() from exc
    except httpx.HTTPStatusError as exc:
        logger.warning("llm_http_error status=%s", exc.response.status_code)
        raise AIError("AI 서비스 요청 실패") from exc
    except (httpx.RequestError, ValueError, KeyError, IndexError, TypeError) as exc:
        logger.warning("llm_response_error type=%s", type(exc).__name__)
        raise AIError("AI 서비스 응답 오류") from exc
