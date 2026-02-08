from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.dependencies.auth import verify_api_key
from src.infrastructure.database import get_session
from src.main import create_app

TEST_API_KEY = "test-api-key"


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def app(mock_session: AsyncMock) -> AsyncIterator:
    application = create_app()

    async def _override_session():
        yield mock_session

    async def _override_api_key():
        return TEST_API_KEY

    application.dependency_overrides[get_session] = _override_session
    application.dependency_overrides[verify_api_key] = _override_api_key

    yield application

    application.dependency_overrides.clear()


@pytest.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_client(app) -> AsyncIterator[AsyncClient]:
    """Client with API key header set."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-Api-Key": TEST_API_KEY},
    ) as ac:
        yield ac
