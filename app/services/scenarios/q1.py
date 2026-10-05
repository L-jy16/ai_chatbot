from app.services.trend import get_hot_issues


async def build_prompt(message: str) -> str:
    """오늘 만들 경제 숏폼을 추천하는 프롬프트입니다."""

    issues = get_hot_issues(limit=10)

    if issues:
        issue_text = "\n".join(
            [
                f"{index + 1}. {item['title']} "
                f"(게시일: {item['pub_date']})"
                for index, item in enumerate(issues)
            ]
        )

    else:
        issue_text = (
            "현재 최신 경제 이슈 데이터를 "
            "불러오지 못했습니다."
        )

    prompt = f"""
당신은 유튜브 경제 숏폼 콘텐츠 기획을 돕는 AI입니다.

사용자 질문:
{message}

현재 수집된 최신 경제 이슈:
{issue_text}

위 데이터를 기반으로 오늘 제작하기 좋은
경제 숏폼 콘텐츠를 추천하세요.

다음 형식으로 답변하세요.

1. 오늘의 주요 경제 이슈
2. 현재 주목할 트렌드
3. 추천 숏폼 주제 3개
4. 가장 추천하는 주제와 이유
5. 숏폼 구성
   - 제목
   - 첫 3초 훅
   - 핵심 내용
   - 마무리

제공된 데이터에 없는 최신 정보를
사실처럼 만들어내지 마세요.
"""

    return prompt.strip()