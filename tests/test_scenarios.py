from app.services.scenarios.q5 import render_prompt as render_q5


def test_q5_uses_only_a_few_titles_and_requires_five_angles():
    issues = [{"title": f"이슈 {index}"} for index in range(8)]

    prompt = render_q5("금리 인하가 너무 흔해", issues)

    assert "반전·비교·논쟁·정보·경험" in prompt
    assert "5~10개" in prompt
    assert "가장 적합한 1개" in prompt
    assert "이슈 4" in prompt
    assert "이슈 5" not in prompt


def test_q5_does_not_claim_live_trend_without_evidence():
    prompt = render_q5("다른 각도", [])

    assert "확인된 최신 이슈 없음" in prompt
    assert "최신 자료가 없으면 그 한계를 밝히세요" in prompt
