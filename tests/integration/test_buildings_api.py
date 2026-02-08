from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from httpx import AsyncClient

BUILDING_UUID_1 = UUID("11111111-1111-1111-1111-111111111111")
BUILDING_UUID_2 = UUID("22222222-2222-2222-2222-222222222222")


def _mock_building(id: UUID = BUILDING_UUID_1, address: str = "Test") -> MagicMock:
    b = MagicMock()
    b.id = id
    b.address = address
    b.latitude = 55.75
    b.longitude = 37.61
    b.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    return b


class TestListBuildings:
    async def test_list_buildings(self, auth_client: AsyncClient) -> None:
        buildings = [
            _mock_building(id=BUILDING_UUID_1),
            _mock_building(id=BUILDING_UUID_2),
        ]
        with patch("src.api.dependencies.services.BuildingRepository") as mock_repo_cls:
            repo = AsyncMock()
            mock_repo_cls.return_value = repo
            repo.get_all.return_value = buildings
            repo.count.return_value = 2

            response = await auth_client.get("/api/v1/buildings/")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    async def test_list_buildings_pagination(self, auth_client: AsyncClient) -> None:
        with patch("src.api.dependencies.services.BuildingRepository") as mock_repo_cls:
            repo = AsyncMock()
            mock_repo_cls.return_value = repo
            repo.get_all.return_value = [_mock_building()]
            repo.count.return_value = 50

            response = await auth_client.get("/api/v1/buildings/", params={"page": 2, "size": 10})

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["size"] == 10
        assert data["total"] == 50
