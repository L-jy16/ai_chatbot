from app.services.trend import (
    compare_periods,
    search_news,
)


async def build_prompt(message: str) -> str:
    """현재 주제를 지금 제작해도 되는지 분석합니다."""

    keyword = message.strip()

    trend_data = compare_periods(keyword)

    news = search_news(
        query=keyword,
        display=5,
    )

    if news:
        news_text = "\n".join(
            [
                f"{index + 1}. {item['title']}"
                for index, item in enumerate(news)
            ]
        )

    else:
        news_text = "관련 최신 뉴스를 불러오지 못했습니다."

    trend_name = {
        "rising": "상승",
        "stable": "유지",
        "falling": "하락",
    }.get(
        trend_data["trend"],
        "판단 불가",
    )

    prompt = f"""
당신은 유튜브 경제 숏폼 콘텐츠 제작을 돕는 AI입니다.

사용자가 입력한 주제:
{message}

검색 트렌드:
- 이전 기간: {trend_data['past']}
- 최근 기간: {trend_data['recent']}
- 추세: {trend_name}

관련 최신 뉴스:
{news_text}

위 데이터를 이용하여 현재 이 주제를
숏폼으로 제작하기 적절한지 분석하세요.

다음 형식으로 답변하세요.

1. 현재 관심도
2. 최근 관련 이슈
3. 과거와 현재 검색 추이 비교
4. 최종 판단
   - 지금 제작 추천
   - 다른 관점으로 제작 추천
   - 현재 우선순위 낮음
5. 추천 제작 방향
   - 제목
   - 핵심 관점
   - 첫 3초 훅

검색 추이는 상대적인 관심도이며
유튜브 조회수를 의미하지 않습니다.

데이터가 부족하면 임의로 판단하지 말고
데이터가 부족하다고 알려주세요.
"""

    return prompt.strip()