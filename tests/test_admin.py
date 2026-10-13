import base64
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.errors import register_error_handlers
from app.models import Chat, User
from app.routers.admin import collect_admin_data, create_admin_router, mask_email

ADMIN = ("admin", "S3cret-pass!")


def basic(username, password):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


@pytest.fixture
def admin_client(session_factory):
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(create_admin_router(get_db=get_db, username=ADMIN[0], password=ADMIN[1]))

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def seeded(db_session):
    now = datetime.now(UTC).replace(tzinfo=None)  # DB의 created_at처럼 UTC 기준 naive 시각
    alice = User(email="alice@example.com", password_hash="x" * 60)
    bo = User(email="bo@example.com", password_hash="x" * 60)
    db_session.add_all([alice, bo])
    db_session.flush()
    db_session.add_all([
        Chat(user_id=alice.id, mode="q1", question="금리 주제 어때?", answer="좋아요", status="success", created_at=now),
        Chat(user_id=alice.id, mode="q3", question="가" * 100, answer=None, status="timeout", created_at=now),
        Chat(user_id=bo.id, mode="free", question="<script>alert(1)</script>", answer=None, status="error",
             created_at=now - timedelta(days=3)),
    ])
    db_session.commit()
    return db_session


def test_main_app_hides_admin_without_account(client):
    assert client.get("/admin", headers=basic(*ADMIN)).status_code == 404


@pytest.mark.parametrize("username,password", [("", ""), ("admin", ""), ("", "S3cret-pass!")])
def test_router_is_not_created_without_both_values(username, password):
    assert create_admin_router(get_db=get_db, username=username, password=password) is None


def test_admin_requires_basic_auth(admin_client):
    response = admin_client.get("/admin")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"


@pytest.mark.parametrize("username,password", [("admin", "wrong"), ("other", "S3cret-pass!")])
def test_admin_rejects_wrong_account(admin_client, username, password):
    assert admin_client.get("/admin", headers=basic(username, password)).status_code == 401


def test_auth_is_checked_before_query_validation(admin_client):
    # 인증 전에는 입력 오류(422)로도 화면 존재나 규칙을 드러내지 않는다.
    assert admin_client.get("/admin?limit=0").status_code == 401


def test_summary_counts(seeded):
    summary = collect_admin_data(seeded, None, 50)["summary"]
    assert summary["users"] == 2
    assert summary["chats"] == 3
    assert summary["chats_24h"] == 2
    assert summary["by_status"] == {"success": 1, "timeout": 1, "error": 1}
    assert summary["by_mode"] == {"free": 1, "q1": 1, "q3": 1}


def test_recent_chats_are_newest_first_masked_and_previewed(seeded):
    chats = collect_admin_data(seeded, None, 50)["chats"]
    assert [c["status"] for c in chats] == ["error", "timeout", "success"]
    assert chats[2]["user"] == "al***@example.com"
    assert chats[1]["question"] == "가" * 80 + "…"
    assert chats[2]["answer_length"] == len("좋아요")
    assert chats[1]["answer_length"] == 0


def test_status_filter_and_limit(seeded):
    assert [c["status"] for c in collect_admin_data(seeded, "error", 50)["chats"]] == ["error"]
    assert len(collect_admin_data(seeded, None, 1)["chats"]) == 1


def test_recent_users_are_masked(seeded):
    users = collect_admin_data(seeded, None, 50)["users"]
    assert [u["email"] for u in users] == ["b***@example.com", "al***@example.com"]


@pytest.mark.parametrize("email,masked", [
    ("creator@example.com", "cr***@example.com"),
    ("ab@example.com", "a***@example.com"),
    ("a@example.com", "a***@example.com"),
])
def test_mask_email(email, masked):
    assert mask_email(email) == masked


def test_page_renders_safely(admin_client, seeded):
    response = admin_client.get("/admin", headers=basic(*ADMIN))
    assert response.status_code == 200
    html = response.text
    assert "alice@example.com" not in html and "al***@example.com" in html
    assert "<script>alert(1)</script>" not in html and "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "가" * 81 not in html
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-robots-tag"] == "noindex, nofollow"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_page_status_filter(admin_client, seeded):
    html = admin_client.get("/admin?status=timeout", headers=basic(*ADMIN)).text
    assert "가" * 80 in html
    assert "금리 주제 어때?" not in html


@pytest.mark.parametrize("query", ["limit=0", "limit=201", "status=unknown"])
def test_invalid_query_is_rejected(admin_client, query):
    assert admin_client.get(f"/admin?{query}", headers=basic(*ADMIN)).status_code == 422


def test_empty_database_page(admin_client):
    response = admin_client.get("/admin", headers=basic(*ADMIN))
    assert response.status_code == 200
    assert "기록이 없습니다" in response.text
