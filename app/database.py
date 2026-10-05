from collections.abc import Iterator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """모든 모델의 부모 클래스."""


def create_db_engine(url: str) -> Engine:
    """DB 엔진을 만든다. SQLite면 스레드 검사를 끄고 외래키 제약을 켠다."""
    is_sqlite = url.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    engine = create_engine(url, connect_args=connect_args)

    if is_sqlite:

        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = create_db_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db() -> Iterator[Session]:
    """요청마다 DB 세션을 열고, 요청이 끝나면 닫는다. commit은 각 라우터에서 한다."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
