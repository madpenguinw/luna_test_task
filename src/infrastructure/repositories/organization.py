from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.domain.models import Organization, organization_activity
from src.infrastructure.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Organization, session)

    def _base_query(self) -> Select[Any]:
        """Base query with eager loading of relationships."""
        return select(Organization).options(
            joinedload(Organization.building),
            selectinload(Organization.activities),
        )

    async def get_by_id_full(self, org_id: UUID) -> Organization | None:
        stmt = self._base_query().where(Organization.id == org_id)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def find_by_building_id(
        self, building_id: UUID, *, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[Organization], int]:
        base_filter = Organization.building_id == building_id

        stmt = self._base_query().where(base_filter).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        items = result.scalars().unique().all()

        total = await self.count(select(Organization).where(base_filter))
        return items, total

    async def find_by_activity_ids(
        self, activity_ids: list[UUID], *, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[Organization], int]:
        """Find organizations that have any of the given activity IDs."""
        base = (
            select(Organization.id)
            .join(organization_activity)
            .where(organization_activity.c.activity_id.in_(activity_ids))
            .distinct()
        )

        count_stmt = select(func.count()).select_from(base.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        subq = base.offset(offset).limit(limit).subquery()
        stmt = self._base_query().where(Organization.id.in_(select(subq)))
        result = await self._session.execute(stmt)
        items = result.scalars().unique().all()

        return items, total

    async def find_by_building_ids(
        self, building_ids: list[UUID], *, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[Organization], int]:
        """Find organizations in given buildings."""
        base_filter = Organization.building_id.in_(building_ids)

        count_stmt = select(func.count()).select_from(
            select(Organization).where(base_filter).subquery()
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = self._base_query().where(base_filter).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        items = result.scalars().unique().all()

        return items, total

    async def search_by_name(
        self, name: str, *, offset: int = 0, limit: int = 100
    ) -> tuple[Sequence[Organization], int]:
        """Search organizations by name (case-insensitive partial match)."""
        pattern = f"%{name}%"
        base_filter = Organization.name.ilike(pattern)

        count_stmt = select(func.count()).select_from(
            select(Organization).where(base_filter).subquery()
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = self._base_query().where(base_filter).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        items = result.scalars().unique().all()

        return items, total
