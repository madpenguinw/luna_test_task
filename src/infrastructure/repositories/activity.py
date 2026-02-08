from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import Activity
from src.infrastructure.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Activity, session)

    async def get_subtree_ids(self, activity_id: UUID) -> list[UUID]:
        base = (
            select(Activity.id, Activity.parent_id)
            .where(Activity.id == activity_id)
            .cte(name="activity_tree", recursive=True)
        )

        recursive = select(Activity.id, Activity.parent_id).join(
            base, Activity.parent_id == base.c.id
        )

        cte = base.union_all(recursive)
        stmt = select(cte.c.id)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())
