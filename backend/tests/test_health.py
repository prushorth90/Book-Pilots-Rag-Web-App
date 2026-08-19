from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.main import app


@pytest.mark.asyncio
async def test_health_check_verifies_database() -> None:
    session = AsyncMock(spec=AsyncSession)

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "connected"}
    session.execute.assert_awaited_once()
