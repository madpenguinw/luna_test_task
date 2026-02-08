from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from src.domain.models.building import Building
from src.services.building import BuildingService

BUILDING_UUID_1 = UUID("11111111-1111-1111-1111-111111111111")
BUILDING_UUID_2 = UUID("22222222-2222-2222-2222-222222222222")


def _make_building(
    id: UUID = BUILDING_UUID_1,
    address: str = "Test Address",
) -> MagicMock:
    b = MagicMock(spec=Building)
    b.id = id
    b.address = address
    b.latitude = 55.75
    b.longitude = 37.61
    b.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    return b


@pytest.fixture
def repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(repo: AsyncMock) -> BuildingService:
    return BuildingService(repository=repo)


class TestGetAll:
    async def test_returns_paginated_response(
        self, service: BuildingService, repo: AsyncMock
    ) -> None:
        buildings = [_make_building(id=BUILDING_UUID_1), _make_building(id=BUILDING_UUID_2)]
        repo.get_all.return_value = buildings
        repo.count.return_value = 2

        result = await service.get_all(page=1, size=20)

        assert result.total == 2
        assert result.page == 1
        assert result.size == 20
        assert result.pages == 1
        assert len(result.items) == 2

    async def test_pagination_offset_calculated(
        self, service: BuildingService, repo: AsyncMock
    ) -> None:
        repo.get_all.return_value = []
        repo.count.return_value = 0

        await service.get_all(page=3, size=10)

        repo.get_all.assert_called_once_with(offset=20, limit=10)
