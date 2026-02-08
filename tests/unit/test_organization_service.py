from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from src.domain.exceptions import NotFoundError
from src.domain.models.organization import Organization
from src.domain.schemas.geo import GeoCircleParams, GeoRectParams
from src.services.organization import OrganizationService

ORG_UUID = UUID("11111111-1111-1111-1111-111111111111")
BUILDING_UUID = UUID("22222222-2222-2222-2222-222222222222")
ACTIVITY_UUID = UUID("33333333-3333-3333-3333-333333333333")
ACTIVITY_UUID_2 = UUID("44444444-4444-4444-4444-444444444444")
ACTIVITY_UUID_3 = UUID("55555555-5555-5555-5555-555555555555")


def _make_org(id: UUID = ORG_UUID, name: str = "Test Org") -> MagicMock:
    org = MagicMock(spec=Organization)
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


def _make_building(id: UUID = BUILDING_UUID) -> MagicMock:
    b = MagicMock()
    b.id = id
    return b


@pytest.fixture
def org_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def building_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def activity_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(
    org_repo: AsyncMock,
    building_repo: AsyncMock,
    activity_repo: AsyncMock,
) -> OrganizationService:
    return OrganizationService(
        organization_repo=org_repo,
        building_repo=building_repo,
        activity_repo=activity_repo,
    )


class TestGetById:
    async def test_returns_organization(
        self, service: OrganizationService, org_repo: AsyncMock
    ) -> None:
        org_repo.get_by_id_full.return_value = _make_org()

        result = await service.get_by_id(ORG_UUID)

        assert result.id == ORG_UUID
        assert result.name == "Test Org"

    async def test_raises_not_found(
        self, service: OrganizationService, org_repo: AsyncMock
    ) -> None:
        org_repo.get_by_id_full.return_value = None

        with pytest.raises(NotFoundError):
            await service.get_by_id(ORG_UUID)


class TestGetByBuilding:
    async def test_returns_orgs_in_building(
        self,
        service: OrganizationService,
        org_repo: AsyncMock,
        building_repo: AsyncMock,
    ) -> None:
        building_repo.get_by_id.return_value = _make_building()
        org_repo.find_by_building_id.return_value = ([_make_org()], 1)

        result = await service.get_by_building(BUILDING_UUID, page=1, size=20)

        assert result.total == 1
        assert len(result.items) == 1

    async def test_raises_not_found_for_building(
        self,
        service: OrganizationService,
        building_repo: AsyncMock,
    ) -> None:
        building_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            await service.get_by_building(BUILDING_UUID)


class TestGetByActivity:
    async def test_returns_orgs_by_activity(
        self,
        service: OrganizationService,
        org_repo: AsyncMock,
        activity_repo: AsyncMock,
    ) -> None:
        activity_repo.get_by_id.return_value = MagicMock()
        org_repo.find_by_activity_ids.return_value = ([_make_org()], 1)

        result = await service.get_by_activity(ACTIVITY_UUID, page=1, size=20)

        assert result.total == 1

    async def test_raises_not_found_for_activity(
        self,
        service: OrganizationService,
        activity_repo: AsyncMock,
    ) -> None:
        activity_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            await service.get_by_activity(ACTIVITY_UUID)


class TestSearchByActivityTree:
    async def test_searches_with_subtree(
        self,
        service: OrganizationService,
        org_repo: AsyncMock,
        activity_repo: AsyncMock,
    ) -> None:
        activity_repo.get_by_id.return_value = MagicMock()
        activity_repo.get_subtree_ids.return_value = [
            ACTIVITY_UUID,
            ACTIVITY_UUID_2,
            ACTIVITY_UUID_3,
        ]
        org_repo.find_by_activity_ids.return_value = ([_make_org()], 1)

        result = await service.search_by_activity_tree(ACTIVITY_UUID)

        activity_repo.get_subtree_ids.assert_called_once_with(ACTIVITY_UUID)
        assert result.total == 1


class TestSearchByName:
    async def test_searches_by_name(
        self,
        service: OrganizationService,
        org_repo: AsyncMock,
    ) -> None:
        org_repo.search_by_name.return_value = ([_make_org()], 1)

        result = await service.search_by_name("Test")

        org_repo.search_by_name.assert_called_once_with("Test", offset=0, limit=20)
        assert result.total == 1


class TestFindInRadius:
    async def test_finds_in_radius(
        self,
        service: OrganizationService,
        org_repo: AsyncMock,
        building_repo: AsyncMock,
    ) -> None:
        building = _make_building()
        building_repo.find_in_radius.return_value = [building]
        org_repo.find_by_building_ids.return_value = ([_make_org()], 1)

        params = GeoCircleParams(latitude=55.75, longitude=37.61, radius_km=5)
        result = await service.find_in_radius(params)

        assert result.total == 1

    async def test_empty_when_no_buildings(
        self,
        service: OrganizationService,
        building_repo: AsyncMock,
    ) -> None:
        building_repo.find_in_radius.return_value = []

        params = GeoCircleParams(latitude=0, longitude=0, radius_km=1)
        result = await service.find_in_radius(params)

        assert result.total == 0
        assert result.items == []


class TestFindInRect:
    async def test_finds_in_rect(
        self,
        service: OrganizationService,
        org_repo: AsyncMock,
        building_repo: AsyncMock,
    ) -> None:
        building = _make_building()
        building_repo.find_in_rect.return_value = [building]
        org_repo.find_by_building_ids.return_value = ([_make_org()], 1)

        params = GeoRectParams(
            min_latitude=55.0,
            max_latitude=56.0,
            min_longitude=37.0,
            max_longitude=38.0,
        )
        result = await service.find_in_rect(params)

        assert result.total == 1

    async def test_empty_when_no_buildings(
        self,
        service: OrganizationService,
        building_repo: AsyncMock,
    ) -> None:
        building_repo.find_in_rect.return_value = []

        params = GeoRectParams(
            min_latitude=0,
            max_latitude=1,
            min_longitude=0,
            max_longitude=1,
        )
        result = await service.find_in_rect(params)

        assert result.total == 0
