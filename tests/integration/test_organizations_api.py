from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from httpx import AsyncClient

from src.api.dependencies.auth import verify_api_key

ORG_UUID = UUID("11111111-1111-1111-1111-111111111111")
BUILDING_UUID = UUID("22222222-2222-2222-2222-222222222222")
ACTIVITY_UUID = UUID("33333333-3333-3333-3333-333333333333")


def _mock_org(id: UUID = ORG_UUID, name: str = "Test Org") -> MagicMock:
    org = MagicMock()
    org.id = id
    org.name = name
    org.phone_numbers = ["1-111-111"]
    org.building_id = BUILDING_UUID
    org.created_at = datetime(2025, 1, 1, tzinfo=UTC)

    building = MagicMock()
    building.id = BUILDING_UUID
    building.address = "Test Address"
    building.latitude = 55.75
    building.longitude = 37.61
    building.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    org.building = building

    act = MagicMock()
    act.id = ACTIVITY_UUID
    act.name = "Activity"
    act.parent_id = None
    act.level = 1
    act.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    org.activities = [act]

    return org


def _mock_building(id: UUID = BUILDING_UUID) -> MagicMock:
    b = MagicMock()
    b.id = id
    return b


class TestGetOrganization:
    async def test_get_by_id(self, auth_client: AsyncClient) -> None:
        with (
            patch("src.api.dependencies.services.OrganizationRepository") as org_cls,
            patch("src.api.dependencies.services.BuildingRepository"),
            patch("src.api.dependencies.services.ActivityRepository"),
        ):
            repo = AsyncMock()
            org_cls.return_value = repo
            repo.get_by_id_full.return_value = _mock_org()

            response = await auth_client.get(f"/api/v1/organizations/{ORG_UUID}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(ORG_UUID)
        assert data["name"] == "Test Org"

    async def test_get_not_found(self, auth_client: AsyncClient) -> None:
        with (
            patch("src.api.dependencies.services.OrganizationRepository") as org_cls,
            patch("src.api.dependencies.services.BuildingRepository"),
            patch("src.api.dependencies.services.ActivityRepository"),
        ):
            repo = AsyncMock()
            org_cls.return_value = repo
            repo.get_by_id_full.return_value = None

            response = await auth_client.get(f"/api/v1/organizations/{ORG_UUID}")

        assert response.status_code == 404


class TestGetByBuilding:
    async def test_returns_orgs(self, auth_client: AsyncClient) -> None:
        with (
            patch("src.api.dependencies.services.OrganizationRepository") as org_cls,
            patch("src.api.dependencies.services.BuildingRepository") as bldg_cls,
            patch("src.api.dependencies.services.ActivityRepository"),
        ):
            org_repo = AsyncMock()
            org_cls.return_value = org_repo
            bldg_repo = AsyncMock()
            bldg_cls.return_value = bldg_repo

            bldg_repo.get_by_id.return_value = _mock_building()
            org_repo.find_by_building_id.return_value = ([_mock_org()], 1)

            response = await auth_client.get(f"/api/v1/organizations/by-building/{BUILDING_UUID}")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    async def test_building_not_found(self, auth_client: AsyncClient) -> None:
        with (
            patch("src.api.dependencies.services.OrganizationRepository"),
            patch("src.api.dependencies.services.BuildingRepository") as bldg_cls,
            patch("src.api.dependencies.services.ActivityRepository"),
        ):
            bldg_repo = AsyncMock()
            bldg_cls.return_value = bldg_repo
            bldg_repo.get_by_id.return_value = None

            response = await auth_client.get(f"/api/v1/organizations/by-building/{BUILDING_UUID}")

        assert response.status_code == 404


class TestGetByActivity:
    async def test_returns_orgs(self, auth_client: AsyncClient) -> None:
        with (
            patch("src.api.dependencies.services.OrganizationRepository") as org_cls,
            patch("src.api.dependencies.services.BuildingRepository"),
            patch("src.api.dependencies.services.ActivityRepository") as act_cls,
        ):
            org_repo = AsyncMock()
            org_cls.return_value = org_repo
            act_repo = AsyncMock()
            act_cls.return_value = act_repo

            act_repo.get_by_id.return_value = MagicMock()
            org_repo.find_by_activity_ids.return_value = ([_mock_org()], 1)

            response = await auth_client.get(f"/api/v1/organizations/by-activity/{ACTIVITY_UUID}")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    async def test_activity_not_found(self, auth_client: AsyncClient) -> None:
        with (
            patch("src.api.dependencies.services.OrganizationRepository"),
            patch("src.api.dependencies.services.BuildingRepository"),
            patch("src.api.dependencies.services.ActivityRepository") as act_cls,
        ):
            act_repo = AsyncMock()
            act_cls.return_value = act_repo
            act_repo.get_by_id.return_value = None

            response = await auth_client.get(f"/api/v1/organizations/by-activity/{ACTIVITY_UUID}")

        assert response.status_code == 404


class TestSearchByName:
    async def test_search_by_name(self, auth_client: AsyncClient) -> None:
        with (
            patch("src.api.dependencies.services.OrganizationRepository") as org_cls,
            patch("src.api.dependencies.services.BuildingRepository"),
            patch("src.api.dependencies.services.ActivityRepository"),
        ):
            repo = AsyncMock()
            org_cls.return_value = repo
            repo.search_by_name.return_value = ([_mock_org()], 1)

            response = await auth_client.get(
                "/api/v1/organizations/search/by-name",
                params={"name": "Test"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    async def test_search_requires_name(self, auth_client: AsyncClient) -> None:
        response = await auth_client.get("/api/v1/organizations/search/by-name")
        assert response.status_code == 422


class TestSearchByActivityTree:
    async def test_search_with_subtree(self, auth_client: AsyncClient) -> None:
        with (
            patch("src.api.dependencies.services.OrganizationRepository") as org_cls,
            patch("src.api.dependencies.services.BuildingRepository"),
            patch("src.api.dependencies.services.ActivityRepository") as act_cls,
        ):
            org_repo = AsyncMock()
            org_cls.return_value = org_repo
            act_repo = AsyncMock()
            act_cls.return_value = act_repo

            act_repo.get_by_id.return_value = MagicMock()
            act_repo.get_subtree_ids.return_value = [
                ACTIVITY_UUID,
                UUID("44444444-4444-4444-4444-444444444444"),
            ]
            org_repo.find_by_activity_ids.return_value = ([_mock_org()], 1)

            response = await auth_client.get(
                f"/api/v1/organizations/search/by-activity-tree/{ACTIVITY_UUID}"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1


class TestSearchInRadius:
    async def test_finds_orgs_in_radius(self, auth_client: AsyncClient) -> None:
        with (
            patch("src.api.dependencies.services.OrganizationRepository") as org_cls,
            patch("src.api.dependencies.services.BuildingRepository") as bldg_cls,
            patch("src.api.dependencies.services.ActivityRepository"),
        ):
            org_repo = AsyncMock()
            org_cls.return_value = org_repo
            bldg_repo = AsyncMock()
            bldg_cls.return_value = bldg_repo

            bldg_repo.find_in_radius.return_value = [_mock_building()]
            org_repo.find_by_building_ids.return_value = ([_mock_org()], 1)

            response = await auth_client.get(
                "/api/v1/organizations/search/in-radius",
                params={"latitude": 55.75, "longitude": 37.61, "radius_km": 5},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    async def test_empty_when_no_buildings(self, auth_client: AsyncClient) -> None:
        with (
            patch("src.api.dependencies.services.OrganizationRepository"),
            patch("src.api.dependencies.services.BuildingRepository") as bldg_cls,
            patch("src.api.dependencies.services.ActivityRepository"),
        ):
            bldg_repo = AsyncMock()
            bldg_cls.return_value = bldg_repo
            bldg_repo.find_in_radius.return_value = []

            response = await auth_client.get(
                "/api/v1/organizations/search/in-radius",
                params={"latitude": 0, "longitude": 0, "radius_km": 1},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0


class TestSearchInRect:
    async def test_finds_orgs_in_rect(self, auth_client: AsyncClient) -> None:
        with (
            patch("src.api.dependencies.services.OrganizationRepository") as org_cls,
            patch("src.api.dependencies.services.BuildingRepository") as bldg_cls,
            patch("src.api.dependencies.services.ActivityRepository"),
        ):
            org_repo = AsyncMock()
            org_cls.return_value = org_repo
            bldg_repo = AsyncMock()
            bldg_cls.return_value = bldg_repo

            bldg_repo.find_in_rect.return_value = [_mock_building()]
            org_repo.find_by_building_ids.return_value = ([_mock_org()], 1)

            response = await auth_client.get(
                "/api/v1/organizations/search/in-rect",
                params={
                    "min_latitude": 55.0,
                    "max_latitude": 56.0,
                    "min_longitude": 37.0,
                    "max_longitude": 38.0,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1


class TestAuthentication:
    async def test_missing_api_key(self, app, client: AsyncClient) -> None:
        """Test that requests without API key are rejected."""
        app.dependency_overrides.pop(verify_api_key, None)

        response = await client.get("/api/v1/buildings/")

        assert response.status_code in (403, 422)

    async def test_invalid_api_key(self, app, client: AsyncClient) -> None:
        """Test that requests with wrong API key are rejected."""
        app.dependency_overrides.pop(verify_api_key, None)

        response = await client.get(
            "/api/v1/buildings/",
            headers={"X-Api-Key": "wrong-key"},
        )

        assert response.status_code == 403


class TestHealthCheck:
    async def test_health_endpoint(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
