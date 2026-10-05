from app.services.scenarios.common import RULES, topic_evidence


async def build_prompt(message: str, keyword: str | None = None) -> str:
    evidence = await topic_evidence(message, keyword)
    return RULES + '\n' + evidence + '''
Q5 다음 편 기획: 질문 또는 이전 대화에서 이전 영상의 주제를 확인하세요.
이전 주제가 없다면 먼저 무엇을 올렸는지 질문하고 과거 영상을 만들어내지 마세요.
주제가 있으면 관련 키워드와 파생 이슈를 바탕으로 후속 후보 3개를 제시하세요.
1편 → 2편 → 3편의 시리즈 구조를 설계하고 각 편의 제목·첫 3초 훅·핵심 내용·다음 편 연결점을 적으세요.
이미 올린 편을 구분하고 오늘 올릴 다음 편 1개와 선정 이유를 제안하세요.
오늘 이슈를 확인할 자료가 없으면 시의성을 단정하지 마세요.
'''
