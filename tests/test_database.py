from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import create_db_engine, engine, get_db


def test_sqlite_engine_enforces_foreign_keys(tmp_path):
    test_engine = create_db_engine(f"sqlite:///{tmp_path / 'fk.db'}")
    with test_engine.connect() as conn:
        assert conn.execute(text("PRAGMA foreign_keys")).scalar() == 1
    test_engine.dispose()


def test_get_db_yields_session_bound_to_app_engine():
    gen = get_db()
    db = next(gen)
    try:
        assert isinstance(db, Session)
        assert db.get_bind() is engine
    finally:
        gen.close()
