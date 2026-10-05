import httpx

from app.config import settings
from app.models import User
from app.services import llm


def test_real_auth_pages_and_static_assets_are_registered(client):
    for path in ['/login', '/signup', '/static/css/style.css', '/static/js/auth.js']:
        assert client.get(path).status_code == 200
    assert '미리보기 모드' not in client.get('/login').text
    assert 'demo@example.com' not in client.get('/login').text


def test_signup_login_pages_and_logout_use_real_auth(client, signup, login, db_session):
    assert client.get('/', follow_redirects=False).headers['location'] == '/login'
    assert signup().status_code == 201
    assert db_session.query(User).count() == 1
    assert login().status_code == 200
    response = client.get('/')
    assert response.status_code == 200
    assert '아이디어 작업실' in response.text
    assert 'id="logout-button"' in response.text
    assert client.get('/history').status_code == 200
    assert client.post('/api/auth/logout').status_code == 204
    assert client.get('/', follow_redirects=False).headers['location'] == '/login'
    assert client.get('/history', follow_redirects=False).headers['location'] == '/login'


def test_signed_in_auth_pages_redirect(logged_in_client):
    for path in ['/login', '/signup']:
        response = logged_in_client.get(path, follow_redirects=False)
        assert response.status_code == 303
        assert response.headers['location'] == '/'


def test_deleted_user_cannot_access_private_pages(logged_in_client, db_session):
    user = db_session.query(User).one()
    db_session.delete(user)
    db_session.commit()
    response = logged_in_client.get('/', follow_redirects=False)
    assert response.status_code == 303
    assert response.headers['location'] == '/login'
    assert logged_in_client.get('/login').status_code == 200
    assert logged_in_client.get('/api/me/chats').status_code == 401


def test_chat_apis_require_real_login(client):
    assert client.post('/api/chat', json={'mode': 'q1', 'message': '질문'}).status_code == 401
    assert client.get('/api/me/chats').status_code == 401


def test_real_chat_failure_is_saved_and_visible_in_history(logged_in_client):
    # 테스트 설정에서 LLM_API_KEY가 비어 있으므로 외부 API를 호출하지 않는다.
    chat = logged_in_client.post('/api/chat', json={'mode': 'free', 'message': '질문'})
    assert chat.status_code == 502
    assert chat.json()['error'] == 'AI_ERROR'
    history = logged_in_client.get('/api/me/chats')
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]['question'] == '질문'
    assert history.json()[0]['status'] == 'error'
    page = logged_in_client.get('/')
    assert 'id="send-button" class="button" type="submit" disabled' not in page.text


def test_real_chat_answer_is_visible_in_history_without_external_call(logged_in_client, monkeypatch):
    monkeypatch.setattr(settings, 'LLM_API_KEY', 'test-only')
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={'choices': [{'message': {'content': '추천 답변'}}]})
    )
    original_client = httpx.AsyncClient
    monkeypatch.setattr(llm.httpx, 'AsyncClient', lambda **kwargs: original_client(transport=transport, **kwargs))

    chat = logged_in_client.post('/api/chat', json={'mode': 'free', 'message': '금리 질문'})
    assert chat.status_code == 200
    assert chat.json()['answer'] == '추천 답변'
    history = logged_in_client.get('/api/me/chats').json()
    assert len(history) == 1
    assert history[0]['id'] == chat.json()['chat_id']
    assert history[0]['question'] == '금리 질문'
    assert history[0]['answer'] == '추천 답변'
    assert history[0]['status'] == 'success'
