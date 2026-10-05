import os
import logging
from datetime import datetime, timedelta

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
    
def get_hot_issues(limit: int = 10) -> list[dict]:
    """최신 경제 뉴스를 오늘의 경제 이슈로 반환합니다."""

    if limit < 1:
        return []

    issues = search_news(
        query="경제",
        display=min(limit, 100),
    )

    return issues[:limit]

def _request_datalab(
    keyword: str,
    start_date: str,
    end_date: str,
) -> list[dict]:
    """네이버 데이터랩에서 검색어 추이를 조회합니다."""

    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        logger.warning("네이버 API 키가 설정되지 않았습니다.")
        return []

    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": [
            {
                "groupName": keyword,
                "keywords": [keyword],
            }
        ],
    }

    try:
        response = requests.post(
            NAVER_DATALAB_URL,
            headers=_get_headers(),
            json=body,
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if not results:
            return []

        return results[0].get("data", [])

    except requests.RequestException as error:
        logger.error(
            "네이버 데이터랩 API 호출 실패: %s",
            error,
        )

        return []
    
def _average_ratio(data: list[dict]) -> float:
    """검색 추이 ratio의 평균을 계산합니다."""

    if not data:
        return 0.0

    values = [
        float(item.get("ratio", 0))
        for item in data
    ]

    if not values:
        return 0.0

    return round(
        sum(values) / len(values),
        2,
    )
    
def compare_periods(keyword: str) -> dict:
    """최근 7일과 이전 7일의 검색 추이를 비교합니다."""

    keyword = keyword.strip()

    if not keyword:
        return {
            "recent": 0.0,
            "past": 0.0,
            "trend": "stable",
        }

    today = datetime.now().date()

    # 최근 7일
    recent_end = today
    recent_start = today - timedelta(days=6)

    # 그 이전 7일
    past_end = recent_start - timedelta(days=1)
    past_start = past_end - timedelta(days=6)

    data = _request_datalab(
        keyword,
        past_start.isoformat(),
        recent_end.isoformat(),
    )

    recent_values = []
    past_values = []

    for item in data:
        period = item.get("period", "")
        ratio = float(item.get("ratio", 0))

        try:
            item_date = datetime.strptime(
                period,
                "%Y-%m-%d",
            ).date()

        except ValueError:
            continue

        if recent_start <= item_date <= recent_end:
            recent_values.append(
                {"ratio": ratio}
            )

        elif past_start <= item_date <= past_end:
            past_values.append(
                {"ratio": ratio}
            )

    recent = _average_ratio(recent_values)
    past = _average_ratio(past_values)

    return {
        "recent": recent,
        "past": past,
        "trend": "stable",
    }