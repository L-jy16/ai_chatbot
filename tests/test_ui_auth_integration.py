from app.models import User


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


def test_pending_apis_still_require_real_login(client):
    assert client.post('/api/chat', json={'mode': 'q1', 'message': '질문'}).status_code == 401
    assert client.get('/api/me/chats').status_code == 401


def test_missing_chat_backend_is_explicit_not_mock(logged_in_client):
    chat = logged_in_client.post('/api/chat', json={'mode': 'q1', 'message': '질문'})
    assert chat.status_code == 503
    assert chat.json()['error'] == 'CHAT_NOT_READY'
    history = logged_in_client.get('/api/me/chats')
    assert history.status_code == 503
    assert history.json()['error'] == 'HISTORY_NOT_READY'
    page = logged_in_client.get('/')
    assert '채팅과 대화 기록 기능은 준비 중' in page.text
    assert 'id="send-button" class="button" type="submit" disabled' in page.text
