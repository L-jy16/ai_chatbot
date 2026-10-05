from app.services.scenarios.common import RULES, topic_evidence


async def build_prompt(message: str, keyword: str | None = None) -> str:
    evidence = await topic_evidence(message, keyword)
    return RULES + '\n' + evidence + '''
Q4 새로운 각도: 사용자가 준 주제에 대해 흔히 다루는 관점을 짚고 차별화된 기획을 제안하세요.
현재 유행은 수집된 자료가 있을 때만 분석하세요. 데이터 부족 시 일반적인 기획안임을 알리세요.
반전형·비교형·논쟁형·정보형·경험형 다섯 유형을 모두 포함해 총 5~10개 주제를 작성하세요.
각 주제에 유형, 제목, 기존 관점과의 차이, 첫 3초 훅을 붙이세요.
논쟁형은 근거 없는 비난이나 사실 왜곡을 피하고, 경험형은 실제 경험을 지어내지 마세요.
끝에 가장 추천하는 1개와 이유, 검증해야 할 사실을 정리하세요.
조회 가능성은 가설이며 실제 조회수를 보장하지 않습니다.
'''
