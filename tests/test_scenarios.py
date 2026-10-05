from app.services.scenarios.q5 import render_prompt as render_q5
from app.services.scenarios.q6 import render_prompt as render_q6


def test_q5_uses_only_a_few_titles_and_requires_five_angles():
    issues = [{"title": f"이슈 {index}"} for index in range(8)]

    prompt = render_q5("금리 인하가 너무 흔해", issues)

    assert "반전·비교·논쟁·정보·경험" in prompt
    assert "5~10개" in prompt
    assert "가장 적합한 1개" in prompt
    assert "이슈 4" in prompt
    assert "이슈 5" not in prompt
    assert "금리 인하가 너무 흔해" not in prompt


def test_q5_does_not_claim_live_trend_without_evidence():
    prompt = render_q5("다른 각도", [])

    assert "확인된 최신 이슈 없음" in prompt
    assert "최신 자료가 없으면 그 한계를 밝히세요" in prompt


def test_q6_requires_previous_topic_and_three_connected_episodes():
    prompt = render_q6("어제 영상 다음 편은?", [{"title": "금리 결정 발표"}])

    assert "기존 주제가 현재 질문이나 이전 대화 어디에도 없으면" in prompt
    assert "1편→2편→3편" in prompt
    assert "오늘 올릴 편 1개" in prompt
    assert "금리 결정 발표" in prompt
    assert "어제 영상 다음 편은?" not in prompt
