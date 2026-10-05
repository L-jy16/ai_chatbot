from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.database import create_db_engine, engine, get_db, upgrade_chat_schema
from app.models import Chat
from app.routers.logs import ChatLog


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


def test_old_chat_schema_keeps_c_mode_and_distinguishes_b_records(tmp_path):
    test_engine = create_db_engine(f"sqlite:///{tmp_path / 'old.db'}")
    with test_engine.begin() as connection:
        connection.execute(text(
            "CREATE TABLE chats (id INTEGER PRIMARY KEY, user_id INTEGER, mode TEXT, "
            "question TEXT, answer TEXT, status TEXT, created_at DATETIME)"
        ))
        connection.execute(text(
            "INSERT INTO chats VALUES (1, 1, 'q4', '금리', '이전 답변', 'success', '2026-10-05 00:00:00')"
        ))
    upgrade_chat_schema(test_engine)
    upgrade_chat_schema(test_engine)
    assert 'scenario_version' in {column['name'] for column in inspect(test_engine).get_columns('chats')}
    with Session(test_engine) as session:
        old_c = session.get(Chat, 1)
        assert old_c.scenario_version == 1
        assert ChatLog.model_validate(old_c).mode == 'q4'
        session.execute(text(
            "INSERT INTO chats (id, user_id, mode, scenario_version, question, answer, status, created_at) "
            "VALUES (2, 1, 'q4', 2, '새 각도', '답변', 'success', '2026-10-05 01:00:00')"
        ))
        session.commit()
        assert ChatLog.model_validate(session.get(Chat, 2)).mode == 'q5'
    test_engine.dispose()
