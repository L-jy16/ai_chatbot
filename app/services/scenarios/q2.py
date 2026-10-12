import asyncio
import json
import re

from app.services import trend
from app.services.scenarios.common import RULES


async def build_prompt(message: str, context: list[str] | None = None) -> str:
    # 화면에서 구조화한 업로드 맥락을 우선 사용. 이전 Q2 질문의 맥락도 재사용한다.
    topics = ''
    for text in [message, *reversed(context or [])]:
        match = re.search(r'최근 업로드 주제:\s*([^\n]+)', text)
        if match and match.group(1).strip():
            topics = match.group(1).strip()
            break
    if not topics:
        return RULES + '''\n운영 채널의 다음 주제를 추천하는 Q2입니다.
질문이나 이전 대화에 과거 업로드 주제가 있으면 이를 바탕으로 연결 아이디어를 제안하세요.
없으면 먼저 '최근 어떤 주제로 영상을 올리셨나요?'라고 질문하고 주제를 받기 전에는 임의로 채널 이력을 만들지 마세요.
현재 외부 데이터를 수집하지 않았으므로 최신 이슈를 확인했다고 말하지 마세요.'''
    keywords = [k.strip()[:50] for k in re.split(r'[,、;]', topics) if k.strip()][:3]
    async def fetch(keyword):
        comparison, news = await asyncio.gather(
            asyncio.to_thread(trend.compare_periods, keyword),
            asyncio.to_thread(trend.search_news, keyword, 3),
        )
        return {'keyword': keyword, 'comparison': comparison, 'news': news}
    evidence = await asyncio.gather(*[fetch(k) for k in keywords])
    data = json.dumps({'previous_topics': topics, 'related_data': evidence}, ensure_ascii=False)
    return RULES + f'''\n<reference_data>{data}</reference_data>
Q2 운영 채널 추천: 기존 업로드 주제와 연결된 최신 정보를 검토하고 오늘 만들 주제를 추천하세요.
1. 기존 영상과의 연결점 2. 관련 최신 자료와 최근/과거 추이 3. 연결 주제 3개
4. 오늘의 추천 1개와 이유 5. 제목·첫 3초 훅·핵심 내용·마무리.
기존 주제를 단순 반복하지 말고 후속 업데이트나 비교 관점을 제안하세요.'''
