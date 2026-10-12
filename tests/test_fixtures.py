import os

import pytest

from app.config import settings
from app.database import get_db
from app.main import app


def test_db_session_uses_temporary_file(db_session, tmp_path):
    assert str(tmp_path) in str(db_session.get_bind().url)


def test_client_overrides_get_db_with_temporary_db(client, db_engine):
    override = app.dependency_overrides[get_db]
    gen = override()
    db = next(gen)
    try:
        assert str(db.get_bind().url) == str(db_engine.url)
    finally:
        gen.close()



def test_app_engine_in_tests_is_in_memory():
    # 팀원이 lifespan을 돌리려고 `with client:`를 써도 실제 ./app.db가 생기면 안 된다.
    # (SQLAlchemy는 상대 경로를 엔진 생성 시점에 절대 경로로 바꾸므로 작업 폴더를 옮겨도 소용없다.)
    from app.database import engine

    assert engine.url.database in (None, "", ":memory:")


@pytest.mark.parametrize("key", ["NAVER_CLIENT_ID", "NAVER_CLIENT_SECRET", "LLM_API_KEY"])
def test_external_api_keys_are_blank_in_tests(key):
    # .env에 실제 키가 있어도 테스트에서는 빈 값이어야 실수로 유료 API를 호출하지 않는다.
    assert os.environ.get(key) == ""
    assert getattr(settings, key) == ""


def _teammate_dependency():
    return "real"


@pytest.fixture
def teammate_override():
    app.dependency_overrides[_teammate_dependency] = lambda: "override"
    yield
    # client fixture가 먼저 정리된 뒤 실행된다. 자기 override(get_db)만 지웠어야 한다.
    assert get_db not in app.dependency_overrides
    assert app.dependency_overrides.pop(_teammate_dependency, None) is not None


def test_client_cleanup_keeps_other_overrides(teammate_override, client):
    assert app.dependency_overrides[_teammate_dependency]() == "override"
