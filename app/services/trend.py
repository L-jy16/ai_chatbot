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