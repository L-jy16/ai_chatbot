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
