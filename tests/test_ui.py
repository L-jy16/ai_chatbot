from pathlib import Path
import sqlite3

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.routers.logs import authenticated_user_id
from app.ui import install_ui
from dev.demo_app import create_demo_app
from scripts.check_logs import read_logs


@pytest.fixture
def client():
    with TestClient(create_demo_app()) as client:
        yield client


@pytest.fixture
def logged_in(client):
    response = client.post('/api/auth/login', json={'email': 'demo@example.com', 'password': 'demo-pass-2026'})
    assert response.status_code == 200
    return client


@pytest.mark.parametrize('path', ['/', '/history'])
def test_private_pages_redirect_without_session(client, path):
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers['location'] == '/login'


@pytest.mark.parametrize('path', ['/login', '/signup'])
def test_public_auth_pages(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']
    assert response.headers['cache-control'] == 'no-store'
    assert "script-src 'self'" in response.headers['content-security-policy']


def test_private_apis_require_login(client):
    assert client.get('/api/me/chats').status_code == 401
    assert client.post('/api/chat', json={'mode': 'q1', 'message': 'hello'}).status_code == 401


def test_history_is_user_scoped_and_does_not_expose_user_id(logged_in):
    response = logged_in.get('/api/me/chats?user_id=2')
    assert response.status_code == 200
    assert response.headers['cache-control'] == 'no-store'
    rows = response.json()
    assert len(rows) == 2
    assert [row['id'] for row in rows] == [1, 2]
    assert rows[1]['answer'] is None
    assert rows[1]['status'] == 'timeout'
    assert all(set(row) == {'id', 'mode', 'question', 'answer', 'status', 'created_at'} for row in rows)
    assert 'PRIVATE USER TWO' not in response.text


@pytest.mark.parametrize('limit', ['0', '-1', '101', 'abc'])
def test_limit_validation(logged_in, limit):
    assert logged_in.get(f'/api/me/chats?limit={limit}').status_code == 422


def test_limit_and_default(logged_in):
    assert len(logged_in.get('/api/me/chats?limit=1').json()) == 1
    assert len(logged_in.get('/api/me/chats').json()) == 2


def test_empty_history(logged_in):
    with logged_in.app.state.demo_session_factory() as db:
        from dev.demo_app import DemoChat
        db.query(DemoChat).filter(DemoChat.user_id == 1).delete()
        db.commit()
    assert logged_in.get('/api/me/chats').json() == []


def test_db_failure_is_recoverable(logged_in, monkeypatch):
    def fail(*args, **kwargs):
        raise OperationalError('SELECT', {}, Exception('unavailable'))
    monkeypatch.setattr(Session, 'execute', fail)
    response = logged_in.get('/api/me/chats')
    assert response.status_code == 503
    assert '기록을 불러오지 못했습니다' in response.json()['detail']


@pytest.mark.parametrize('mode', ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'free'])
def test_each_mode_saves_then_appears_in_history(logged_in, mode):
    response = logged_in.post('/api/chat', json={'mode': mode, 'message': '테스트 질문'})
    assert response.status_code == 200
    row = logged_in.get('/api/me/chats?limit=1').json()[0]
    assert row['id'] == response.json()['chat_id']
    assert row['mode'] == mode
    assert row['question'] == '테스트 질문'
    assert row['answer'] == response.json()['answer']


@pytest.mark.parametrize('message,code,status', [('[timeout]', 'AI_TIMEOUT', 504), ('[error]', 'AI_ERROR', 502)])
def test_failed_response_saved_with_null_answer_and_server_recovers(logged_in, message, code, status):
    response = logged_in.post('/api/chat', json={'mode': 'q3', 'message': message})
    assert response.status_code == status
    assert response.json()['error'] == code
    row = logged_in.get('/api/me/chats?limit=1').json()[0]
    assert row['answer'] is None
    assert row['status'] == ('timeout' if status == 504 else 'error')
    assert logged_in.post('/api/chat', json={'mode': 'q1', 'message': '다시 질문'}).status_code == 200


@pytest.mark.parametrize('message', ['', '  ', '가' * 501])
def test_question_validation(logged_in, message):
    assert logged_in.post('/api/chat', json={'mode': 'q1', 'message': message}).status_code == 422


def test_q2_asks_for_previous_upload_topics_when_missing(logged_in):
    response = logged_in.post('/api/chat', json={'mode': 'q2', 'message': '운영 중인 채널에 뭘 올릴까?'})
    assert response.status_code == 200
    assert '과거에 어떤 주제로 올리셨나요?' in response.json()['answer']


def test_q2_uses_previous_upload_topics_and_saves_context(logged_in):
    message = '최근 업로드 주제: 환율 상승\n질문: 연결된 오늘의 주제를 추천해 줘.'
    response = logged_in.post('/api/chat', json={'mode': 'q2', 'message': message})
    assert response.status_code == 200
    assert '과거 업로드 주제: 환율 상승' in response.json()['answer']
    assert logged_in.get('/api/me/chats?limit=1').json()[0]['question'] == message


def test_unknown_mode_rejected(logged_in):
    assert logged_in.post('/api/chat', json={'mode': 'q7', 'message': '지원하지 않는 번호'}).status_code == 422


def test_logout_revokes_pages_and_api(logged_in):
    assert logged_in.post('/api/auth/logout').status_code == 200
    assert logged_in.get('/api/me/chats').status_code == 401
    assert logged_in.get('/', follow_redirects=False).status_code == 303


def test_tampered_cookie_rejected(client):
    client.cookies.set('pulse_demo_session', 'eyJ1c2VyX2lkIjoyfQ==.forged.signature')
    assert client.get('/api/me/chats').status_code == 401


@pytest.mark.parametrize('value', [None, True, 0, -1, '1', {'id': '1'}, {'user_id': 1}])
def test_invalid_auth_identity_cannot_read_history(value):
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as error:
        authenticated_user_id(value)
    assert error.value.status_code == 401


def test_auth_adapters_accept_integer_dict_and_user_object():
    from types import SimpleNamespace
    assert authenticated_user_id(1) == 1
    assert authenticated_user_id({'id': 2}) == 2
    assert authenticated_user_id(SimpleNamespace(id=3)) == 3


def test_duplicate_install_has_clear_error(client):
    with pytest.raises(RuntimeError, match='only once'):
        install_ui(client.app, require_login=lambda: 1, get_db=lambda: None, chat_model=object)


def test_templates_and_static_assets_render(logged_in):
    for page in ['/', '/history']:
        response = logged_in.get(page)
        assert response.status_code == 200
        assert 'PULSE' in response.text
    for asset in ['css/style.css', 'js/common.js', 'js/auth.js', 'js/chat.js', 'js/modes.js', 'js/history.js']:
        assert logged_in.get(f'/static/{asset}').status_code == 200


def test_sql_script_is_user_scoped_and_latest_first(tmp_path):
    path = tmp_path / 'test.db'
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE chats (id INTEGER, user_id INTEGER, mode TEXT, created_at TEXT, question TEXT, answer TEXT, status TEXT)')
        db.executemany('INSERT INTO chats VALUES (?, ?, ?, ?, ?, ?, ?)', [
            (1, 1, 'q1', '2026-10-05T09:00:00', 'old', 'answer', 'success'),
            (2, 1, 'q3', '2026-10-05T10:00:00', 'new', None, 'timeout'),
            (3, 2, 'q4', '2026-10-05T11:00:00', 'private', 'answer', 'success'),
        ])
    rows = read_logs(path, user_id=1, limit=1)
    assert len(rows) == 1 and rows[0]['id'] == 2
    assert rows[0]['answer'] is None


def test_sql_script_does_not_create_missing_database(tmp_path):
    path = tmp_path / 'missing.db'
    with pytest.raises(sqlite3.OperationalError):
        read_logs(path, user_id=1, limit=20)
    assert not path.exists()
