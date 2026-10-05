import os
import logging

import requests


logger = logging.getLogger(__name__)


NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")

NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"
NAVER_DATALAB_URL = "https://openapi.naver.com/v1/datalab/search"


def _get_headers() -> dict[str, str]:
    """네이버 API 인증 헤더를 반환합니다."""

    return {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
        "Content-Type": "application/json",
    }
    
def _clean_text(text: str) -> str:
    """네이버 뉴스 결과에 포함된 일부 HTML 문자를 정리합니다."""

    return (
        text.replace("<b>", "")
        .replace("</b>", "")
        .replace("&quot;", '"')
        .replace("&amp;", "&")
    )


def search_news(
    query: str = "경제",
    display: int = 10,
) -> list[dict]:
    """네이버 뉴스 검색 API를 호출합니다."""

    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        logger.warning("네이버 API 키가 설정되지 않았습니다.")
        return []

    params = {
        "query": query,
        "display": display,
        "sort": "date",
    }

    try:
        response = requests.get(
            NAVER_NEWS_URL,
            headers=_get_headers(),
            params=params,
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()

        result = []

        for item in data.get("items", []):
            result.append(
                {
                    "title": _clean_text(
                        item.get("title", "")
                    ),
                    "link": (
                        item.get("originallink")
                        or item.get("link", "")
                    ),
                    "pub_date": item.get("pubDate", ""),
                }
            )

        return result

    except requests.RequestException as error:
        logger.error(
            "네이버 뉴스 API 호출 실패: %s",
            error,
        )

        return []