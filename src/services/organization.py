from uuid import UUID

from src.domain.exceptions import NotFoundError
from src.domain.interfaces.repositories import (
    ActivityRepositoryProtocol,
    BuildingRepositoryProtocol,
    OrganizationRepositoryProtocol,
)
from src.domain.schemas.geo import GeoCircleParams, GeoRectParams
from src.domain.schemas.organization import OrganizationRead
from src.domain.schemas.pagination import PaginatedResponse
from src.services.pagination import paginate


class OrganizationService:
    def __init__(
        self,
        organization_repo: OrganizationRepositoryProtocol,
        building_repo: BuildingRepositoryProtocol,
        activity_repo: ActivityRepositoryProtocol,
    ) -> None:
        self._org_repo = organization_repo
        self._building_repo = building_repo
        self._activity_repo = activity_repo

    async def get_by_id(self, org_id: UUID) -> OrganizationRead:
        org = await self._org_repo.get_by_id_full(org_id)
        if org is None:
            raise NotFoundError("Organization", org_id)
        return OrganizationRead.model_validate(org)

    async def get_by_building(
        self, building_id: UUID, *, page: int = 1, size: int = 20
    ) -> PaginatedResponse[OrganizationRead]:
        building = await self._building_repo.get_by_id(building_id)
        if building is None:
            raise NotFoundError("Building", building_id)

        offset = (page - 1) * size
        items, total = await self._org_repo.find_by_building_id(
            building_id, offset=offset, limit=size
        )
        return paginate(items, total, page, size, OrganizationRead)

    async def get_by_activity(
        self, activity_id: UUID, *, page: int = 1, size: int = 20
    ) -> PaginatedResponse[OrganizationRead]:
        """Get organizations by a specific activity."""
        activity = await self._activity_repo.get_by_id(activity_id)
        if activity is None:
            raise NotFoundError("Activity", activity_id)

        offset = (page - 1) * size
        items, total = await self._org_repo.find_by_activity_ids(
            [activity_id], offset=offset, limit=size
        )
        return paginate(items, total, page, size, OrganizationRead)

    async def search_by_activity_tree(
        self, activity_id: UUID, *, page: int = 1, size: int = 20
    ) -> PaginatedResponse[OrganizationRead]:
        """Search organizations by activity including all child activities."""
        activity = await self._activity_repo.get_by_id(activity_id)
        if activity is None:
            raise NotFoundError("Activity", activity_id)

        subtree_ids = await self._activity_repo.get_subtree_ids(activity_id)
        offset = (page - 1) * size
        items, total = await self._org_repo.find_by_activity_ids(
            subtree_ids, offset=offset, limit=size
        )
        return paginate(items, total, page, size, OrganizationRead)

    async def search_by_name(
        self, name: str, *, page: int = 1, size: int = 20
    ) -> PaginatedResponse[OrganizationRead]:
        offset = (page - 1) * size
        items, total = await self._org_repo.search_by_name(name, offset=offset, limit=size)
        return paginate(items, total, page, size, OrganizationRead)

    async def find_in_radius(
        self, params: GeoCircleParams, *, page: int = 1, size: int = 20
    ) -> PaginatedResponse[OrganizationRead]:
        buildings = await self._building_repo.find_in_radius(params)
        if not buildings:
            return paginate([], 0, page, size, OrganizationRead)

        building_ids = [b.id for b in buildings]
        offset = (page - 1) * size
        items, total = await self._org_repo.find_by_building_ids(
            building_ids, offset=offset, limit=size
        )
        return paginate(items, total, page, size, OrganizationRead)

    async def find_in_rect(
        self, params: GeoRectParams, *, page: int = 1, size: int = 20
    ) -> PaginatedResponse[OrganizationRead]:
        if params.is_too_wide:
            buildings = await self._building_repo.get_all()
        else:
            buildings = await self._building_repo.find_in_rect(params)

        if not buildings:
            return paginate([], 0, page, size, OrganizationRead)

        building_ids = [b.id for b in buildings]
        offset = (page - 1) * size
        items, total = await self._org_repo.find_by_building_ids(
            building_ids, offset=offset, limit=size
        )
        return paginate(items, total, page, size, OrganizationRead)
