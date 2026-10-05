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
