from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select

from app.models import Chat
from app.routers import chat
from app.services import llm


@pytest.fixture
def ai(monkeypatch):
    monkeypatch.setattr(chat.q1, 'build_prompt', AsyncMock(return_value='Q1 prompt'))

    for scenario in (chat.q2, chat.q3, chat.q4, chat.q5):
        monkeypatch.setattr(scenario, 'build_prompt', AsyncMock(return_value='scenario prompt'))
    mock = AsyncMock(return_value='추천 주제와 데이터 한계')
    monkeypatch.setattr(llm, 'ask_llm', mock)
    return mock


def test_chat_requires_login(client, ai):
    assert client.post('/api/chat', json={'mode':'q1','message':'오늘 주제'}).status_code == 401
    ai.assert_not_called()


@pytest.mark.parametrize('body', [
    {'mode':'q1','message':'  '}, {'mode':'q4','message':'x'*501},
    {'mode':'q6','message':'주제'}, {'mode':'q4','message':'주제','keyword':'x'*51},
])
def test_chat_validation(logged_in_client, ai, body):
    assert logged_in_client.post('/api/chat', json=body).status_code == 422
    ai.assert_not_called()


def test_chat_saves_and_uses_previous_context(logged_in_client, db_session, ai):
    for i in range(7):
        response = logged_in_client.post('/api/chat', json={'mode':'q1','message':f'주제 {i}'})
        assert response.status_code == 200
    record = db_session.get(Chat, response.json()['chat_id'])
    assert record.status == 'success'
    assert record.answer == '추천 주제와 데이터 한계'
    messages = ai.call_args.args[1]
    assert len(messages) == 11
    assert messages[0]['content'] == '주제 1'
    assert messages[-1]['content'] == '주제 6'
    assert logged_in_client.get('/api/me/chats?limit=2').json()[0]['id'] == record.id


def test_q3_passes_keyword(logged_in_client, ai):
    response=logged_in_client.post('/api/chat', json={'mode':'q3','message':'올려도 돼?','keyword':'금리 인하'})
    assert response.status_code == 200
    chat.q3.build_prompt.assert_awaited_once_with('올려도 돼?', '금리 인하')


@pytest.mark.parametrize('error,code,status', [(llm.AITimeoutError(),504,'timeout'),(llm.AIError(),502,'error')])
def test_ai_failure_is_saved(logged_in_client, db_session, ai, error, code, status):
    ai.side_effect=error
    result=logged_in_client.post('/api/chat',json={'message':'오늘 주제'})
    assert result.status_code==code
    record=db_session.scalar(select(Chat))
    assert record.status==status and record.answer is None
    assert logged_in_client.get('/health').status_code==200


def test_user_history_and_context_are_isolated(client, signup, login, ai):
    signup(); login()
    client.post('/api/chat',json={'message':'사용자1 비공개 주제'})
    client.post('/api/auth/logout')
    signup(email='second@example.com'); login(email='second@example.com')
    assert client.get('/api/me/chats').json()==[]
    client.post('/api/chat',json={'message':'사용자2 주제'})
    assert ai.call_args.args[1]==[{'role':'user','content':'사용자2 주제'}]


def test_static_and_configuration_do_not_expose_keys(logged_in_client):
    assert logged_in_client.get('/').status_code==200
    data=logged_in_client.get('/api/me').json()
    assert 'LLM_API_KEY' not in data
    assert data['trend_configured'] is False
    assert logged_in_client.get('/.env').status_code==404

@pytest.mark.parametrize('mode', ['q1','q2','q3','q4','q5'])
def test_all_ui_modes_are_saved_with_new_version(logged_in_client, db_session, ai, mode):
    response=logged_in_client.post('/api/chat',json={'mode':mode,'message':'최근 업로드 주제: 반도체\n질문: 오늘 주제'})
    assert response.status_code==200
    record=db_session.get(Chat,response.json()['chat_id'])
    assert record.mode==mode and record.scenario_version==2
    assert logged_in_client.get('/api/me/chats').json()[0]['mode']==mode
    getattr(chat,mode).build_prompt.assert_awaited_once()


def test_no_duplicate_ui_or_history_routes():
    from app.main import app
    def paths(router):
        for route in router.routes:
            if hasattr(route, 'original_router'):
                yield from paths(route.original_router)
            else:
                yield getattr(route, 'path', None)
    registered=list(paths(app))
    for path in ('/','/api/me/chats','/api/chat','/static'):
        assert registered.count(path)==1
