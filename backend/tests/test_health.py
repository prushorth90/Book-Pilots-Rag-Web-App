from collections.abc import AsyncGenerator
from typing import Any

from fastapi.testclient import TestClient

from app.database.session import get_db
from app.main import app


class FakeSession:
    async def execute(self, _statement: Any) -> None:
        return None


async def override_db() -> AsyncGenerator[FakeSession, None]:
    yield FakeSession()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def test_health_reports_api_and_database_ready() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}