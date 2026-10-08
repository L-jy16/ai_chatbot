"""네이버 뉴스·검색 추이. 실패를 실제 0이나 보합으로 취급하지 않는다."""
import html
import logging
import math
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests

from app.config import settings

logger = logging.getLogger(__name__)
# 네이버 검색·데이터랩 API는 네이버 클라우드 플랫폼의 NAVER API HUB로 이관되었다.
# 키(Client ID·Secret)는 HUB Application에서 발급하며, 쓰려는 API(뉴스 검색, 검색어 트렌드)를 Application에 켜 두어야 한다.
NAVER_API_HUB = 'https://naverapihub.apigw.ntruss.com'
NAVER_NEWS_URL = f'{NAVER_API_HUB}/search/v1/news'
NAVER_DATALAB_URL = f'{NAVER_API_HUB}/search-trend/v1/search'


def _get_headers() -> dict[str, str]:
    return {'X-NCP-APIGW-API-KEY-ID': settings.NAVER_CLIENT_ID,
            'X-NCP-APIGW-API-KEY': settings.NAVER_CLIENT_SECRET,
            'Content-Type': 'application/json'}


def _request(url: str, *, body=None, params=None) -> dict:
    if not settings.NAVER_CLIENT_ID or not settings.NAVER_CLIENT_SECRET:
        logger.warning('naver_unavailable reason=missing_credentials')
        return {}
    try:
        if body is None:
            response = requests.get(url, headers=_get_headers(), params=params, timeout=settings.NAVER_TIMEOUT_SECONDS)
        else:
            response = requests.post(url, headers=_get_headers(), json=body, timeout=settings.NAVER_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, dict) else {}
    except (requests.RequestException, ValueError) as exc:
        logger.warning('naver_request_failed type=%s', type(exc).__name__)
        return {}


def _clean_text(text: str) -> str:
    return html.unescape(re.sub(r'<[^>]*>', '', text))


def search_news(query: str = '경제', display: int = 10) -> list[dict]:
    if not query.strip() or display < 1:
        return []
    data = _request(NAVER_NEWS_URL, params={'query': query, 'display': min(display, 100), 'sort': 'date'})
    items = data.get('items', [])
    if not isinstance(items, list):
        return []
    return [{'title': _clean_text(str(item.get('title', ''))),
             'link': str(item.get('originallink') or item.get('link') or ''),
             'pub_date': str(item.get('pubDate', ''))}
            for item in items if isinstance(item, dict) and item.get('title')]


def get_hot_issues(limit: int = 10) -> list[dict]:
    # 최신 뉴스 목록이며 인기 순위나 실제 언급량을 뜻하지 않는다.
    return search_news('경제', limit)[:max(0, limit)]


def _request_datalab(keyword: str, start_date: str, end_date: str) -> list[dict]:
    data = _request(NAVER_DATALAB_URL, body={
        'startDate': start_date, 'endDate': end_date, 'timeUnit': 'date',
        'keywordGroups': [{'groupName': keyword, 'keywords': [keyword]}],
    })
    results = data.get('results', [])
    if not isinstance(results, list) or not results or not isinstance(results[0], dict):
        return []
    values = results[0].get('data', [])
    return values if isinstance(values, list) else []


def compare_periods(keyword: str) -> dict:
    # 아직 완료되지 않은 오늘은 제외. 두 기간을 한 번에 요청하여 동일 척도로 비교한다.
    end = datetime.now(ZoneInfo('Asia/Seoul')).date() - timedelta(days=1)
    recent_start = end - timedelta(days=6)
    start = end - timedelta(days=13)
    result = {'recent': None, 'past': None, 'trend': 'unknown', 'available': False,
              'recent_start': recent_start.isoformat(), 'recent_end': end.isoformat(),
              'past_start': start.isoformat(), 'past_end': (recent_start - timedelta(days=1)).isoformat()}
    if not keyword.strip():
        return result
    raw = _request_datalab(keyword.strip(), start.isoformat(), end.isoformat())
    by_date = {}
    for item in raw:
        try:
            day = datetime.strptime(item['period'], '%Y-%m-%d').date()
            ratio = float(item['ratio'])
            if start <= day <= end and math.isfinite(ratio) and 0 <= ratio <= 100:
                by_date[day] = ratio
        except (KeyError, TypeError, ValueError):
            continue
    # 누락값을 0으로 지어내지 않는다. 두 7일 구간이 모두 있어야 비교한다.
    if len(by_date) != 14:
        return result
    recent = sum(v for d, v in by_date.items() if d >= recent_start) / 7
    past = sum(v for d, v in by_date.items() if d < recent_start) / 7
    if not recent and not past:
        return result
    if not past or recent >= past * 1.2:
        trend = 'rising'
    elif recent <= past * 0.8:
        trend = 'falling'
    elif recent >= 80:
        trend = 'peak'
    else:
        trend = 'stable'
    result.update(recent=round(recent, 2), past=round(past, 2), trend=trend, available=True)
    return result


def extract_keyword(message: str) -> str:
    """일반적인 Q4 문장에서 요청 표현을 제거. 화면에서 정확한 키워드 지정도 가능."""
    text = re.sub(r'[?？!]+$', '', message.strip()).strip()
    text = re.split(r'\s*(?:주제(?:를|는|로|가)?\s|지금\s|오늘\s|올려도\s|올릴까|만들어도\s|숏폼으로\s|영상으로\s)', text, maxsplit=1)[0]
    return text.strip(' \"\'“”‘’')[:50]


def issue_keywords(issues: list[dict], limit: int = 3) -> list[str]:
    # 비용·지연을 제한하며 뉴스에 실제 등장한 경제 키워드만 비교한다.
    vocabulary = ['금리', '환율', '인플레이션', '물가', '부동산', '반도체', '코스피', '코스닥',
                  '비트코인', '주식', '관세', '수출', '유가', '인공지능', 'AI', '고용', '연금']
    found = []
    for issue in issues:
        for keyword in vocabulary:
            if keyword.casefold() in issue['title'].casefold() and keyword not in found:
                found.append(keyword)
                if len(found) >= limit:
                    return found
    return found
