import asyncio
from unittest.mock import Mock

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.database import create_db_engine, upgrade_chat_schema
from app.models import Chat
from app.routers.logs import ChatLog
from app.services import trend
from app.services.scenarios import q2, q4, q5


@pytest.fixture
def evidence(monkeypatch):
    compare=Mock(return_value={'recent':None,'past':None,'available':False,'trend':'unknown'})
    news=Mock(return_value=[])
    monkeypatch.setattr(trend,'compare_periods',compare)
    monkeypatch.setattr(trend,'search_news',news)
    return compare, news


def test_q2_asks_for_previous_topics_without_inventing_data(evidence):
    prompt=asyncio.run(q2.build_prompt('추천해 줘'))
    assert '최근 어떤 주제로 영상을 올리셨나요?' in prompt
    evidence[0].assert_not_called()


def test_q2_fetches_related_topics_from_context(evidence):
    prompt=asyncio.run(q2.build_prompt('다른 아이디어도 알려줘',context=['최근 업로드 주제: 반도체, 환율\n질문: 추천해 줘']))
    assert '연결 주제 3개' in prompt
    assert {call.args[0] for call in evidence[0].call_args_list}=={'반도체','환율'}


def test_q4_requires_five_angles_and_no_view_guarantee(evidence):
    prompt=asyncio.run(q4.build_prompt('AI 투자 주제', 'AI 투자'))
    for term in ('반전형','비교형','논쟁형','정보형','경험형','5~10개','보장하지'):
        assert term in prompt
    evidence[0].assert_called_once_with('AI 투자')


def test_q5_requires_series_and_previous_topic(evidence):
    prompt=asyncio.run(q5.build_prompt('어제 환율 영상 다음 편', '환율'))
    assert '1편 → 2편 → 3편' in prompt
    assert '먼저 무엇을 올렸는지 질문' in prompt
    assert '오늘 올릴 다음 편 1개' in prompt


def test_legacy_schema_upgrade_preserves_record_and_is_repeatable(tmp_path):
    engine=create_db_engine(f'sqlite:///{tmp_path / "old.db"}')
    with engine.begin() as conn:
        conn.execute(text('CREATE TABLE chats (id INTEGER PRIMARY KEY, user_id INTEGER, mode TEXT, question TEXT, answer TEXT, status TEXT, created_at DATETIME)'))
        conn.execute(text("INSERT INTO chats VALUES (1,1,'q4','금리','이전 답변','success','2026-10-05 00:00:00')"))
    upgrade_chat_schema(engine)
    upgrade_chat_schema(engine)
    assert 'scenario_version' in {c['name'] for c in inspect(engine).get_columns('chats')}
    with Session(engine) as db:
        row=db.get(Chat,1)
        assert row.mode=='q4' and row.scenario_version==1
        assert row.answer=='이전 답변'
        assert ChatLog.model_validate(row).mode=='q3'
    engine.dispose()
