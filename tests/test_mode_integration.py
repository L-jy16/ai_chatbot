"""화면(D) 모드 번호가 실제 앱에서 저장·조회까지 일관되게 이어지는지 확인한다."""
import pytest
from sqlalchemy import select

from app.models import Chat, User


def test_screen_mode_is_saved_with_screen_numbering(logged_in_client, db_session):
    message = "최근 업로드 주제: 환율 상승\n질문: 오늘 뭐 올릴까?"
    response = logged_in_client.post("/api/chat", json={"mode": "q2", "message": message})

    assert response.status_code == 502  # 테스트에서는 LLM 키가 비어 있어 외부 API를 호출하지 않는다
    row = db_session.scalars(select(Chat)).one()
    assert (row.mode, row.scenario_version) == ("q2", 2)
    assert logged_in_client.get("/api/me/chats").json()[0]["mode"] == "q2"


@pytest.mark.parametrize(
    ("version", "stored", "shown"),
    [
        (1, "q4", "q3"),  # 이전 계획서 번호: Q4 타이밍 → 화면 Q3
        (1, "q6", "q5"),
        (3, "q5", "q4"),  # C 재통합 번호(계획서 번호와 같음): Q5 새로운 각도 → 화면 Q4
        (3, "q6", "q5"),
        (3, "free", "free"),
        (2, "q4", "q4"),  # 화면 번호로 저장된 기록은 그대로
    ],
)
def test_history_shows_legacy_modes_in_screen_numbering(logged_in_client, db_session, version, stored, shown):
    user = db_session.scalars(select(User)).one()
    db_session.add(
        Chat(user_id=user.id, mode=stored, scenario_version=version, question="이전 질문", answer="답", status="success")
    )
    db_session.commit()

    assert logged_in_client.get("/api/me/chats").json()[0]["mode"] == shown
