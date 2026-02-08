from collections.abc import Sequence
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository providing common read operations."""

    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> ModelType | None:
        return await self._session.get(self._model, entity_id)

    async def get_all(self, *, offset: int = 0, limit: int = 100) -> Sequence[ModelType]:
        stmt = select(self._model).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def count(self, stmt: Select[Any] | None = None) -> int:
        if stmt is None:
            count_stmt = select(func.count()).select_from(self._model)
        else:
            count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await self._session.execute(count_stmt)
        return result.scalar_one()
