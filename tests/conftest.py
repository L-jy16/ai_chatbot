import os

# app.config는 import 시점에 Settings()를 만들므로, 앱을 import하기 전에 테스트용 키를 넣는다.
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)
