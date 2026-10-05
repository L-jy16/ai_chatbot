LOGIN_REQUIRED = {"error": "LOGIN_REQUIRED", "message": "로그인이 필요해요."}


def test_logout_returns_204(logged_in_client):
    response = logged_in_client.post("/api/auth/logout")
    assert response.status_code == 204
    assert response.content == b""


def test_logout_twice_requires_login(logged_in_client):
    logged_in_client.post("/api/auth/logout")
    response = logged_in_client.post("/api/auth/logout")
    assert response.status_code == 401
    assert response.json() == LOGIN_REQUIRED


def test_logout_without_login_is_rejected(client):
    response = client.post("/api/auth/logout")
    assert response.status_code == 401
    assert response.json() == LOGIN_REQUIRED
