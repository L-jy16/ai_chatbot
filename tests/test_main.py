from starlette.middleware.sessions import SessionMiddleware

from app.main import app


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_session_middleware_is_installed():
    assert any(middleware.cls is SessionMiddleware for middleware in app.user_middleware)
