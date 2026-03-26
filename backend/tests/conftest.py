import os

import pytest
from fastapi.testclient import TestClient


os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")

from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
