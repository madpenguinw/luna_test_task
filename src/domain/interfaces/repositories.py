from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from src.domain.models.activity import Activity
from src.domain.models.building import Building
from src.domain.models.organization import Organization
from src.domain.schemas.geo import GeoCircleParams, GeoRectParams


class BuildingRepositoryProtocol(Protocol):
    async def get_by_id(self, entity_id: UUID) -> Building | None: ...

    async def get_all(self, *, offset: int = 0, limit: int = 100) -> Sequence[Building]: ...

    async def count(self) -> int: ...

    async def find_in_radius(self, params: GeoCircleParams) -> Sequence[Building]: ...

    async def find_in_rect(self, params: GeoRectParams) -> Sequence[Building]: ...


class ActivityRepositoryProtocol(Protocol):
    async def get_by_id(self, entity_id: UUID) -> Activity | None: ...

    async def get_subtree_ids(self, activity_id: UUID) -> list[UUID]: ...


class OrganizationRepositoryProtocol(Protocol):
    async def get_by_id_full(self, org_id: UUID) -> Organization | None: ...

    async def find_by_building_id(
        self, building_id: UUID, *, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[Organization], int]: ...

    async def find_by_activity_ids(
        self, activity_ids: list[UUID], *, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[Organization], int]: ...

    async def find_by_building_ids(
        self, building_ids: list[UUID], *, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[Organization], int]: ...

    async def search_by_name(
        self, name: str, *, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[Organization], int]: ...
