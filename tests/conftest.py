import os

# app.config는 import 시점에 Settings()를 만들므로, 앱을 import하기 전에 테스트용 키를 넣는다.
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.database import Base, create_db_engine, get_db  # noqa: E402
from app.main import app  # noqa: E402

TEST_EMAIL = "creator@example.com"
TEST_PASSWORD = "shorts1234"


@pytest.fixture
def db_engine(tmp_path):
    """테스트마다 새 SQLite 파일을 만들고 모든 테이블을 생성한다."""
    engine = create_db_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(db_engine):
    return sessionmaker(bind=db_engine, autoflush=False)


@pytest.fixture
def db_session(session_factory):
    """테스트 코드에서 DB 상태를 직접 확인할 때 쓰는 세션."""
    with session_factory() as session:
        yield session


@pytest.fixture
def client(session_factory):
    """임시 DB를 쓰는 TestClient. 실제 app.db는 건드리지 않는다."""

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def signup(client):
    """회원가입 요청을 보내는 함수를 돌려준다. signup(email=..., password=...)"""

    def _signup(email=TEST_EMAIL, password=TEST_PASSWORD):
        return client.post("/api/auth/signup", json={"email": email, "password": password})

    return _signup
