from collections.abc import Sequence

from geoalchemy2 import Geography
from geoalchemy2.functions import (
    ST_DWithin,
    ST_Intersects,
    ST_MakeEnvelope,
    ST_MakePoint,
    ST_SetSRID,
)
from sqlalchemy import ColumnElement, cast, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import Building
from src.domain.schemas import GeoCircleParams, GeoRectParams
from src.infrastructure.repositories.base import BaseRepository

_GEOGRAPHY_4326 = Geography(srid=4326)


class BuildingRepository(BaseRepository[Building]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Building, session)

    async def find_in_radius(self, params: GeoCircleParams) -> Sequence[Building]:
        point = cast(
            ST_SetSRID(ST_MakePoint(params.longitude, params.latitude), 4326),
            _GEOGRAPHY_4326,
        )
        stmt = select(Building).where(ST_DWithin(Building.location, point, params.radius_meters))
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def find_in_rect(self, params: GeoRectParams) -> Sequence[Building]:
        filter_condition = self._build_rect_filter(params)
        stmt = select(Building).where(filter_condition)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    def _build_rect_filter(self, params: GeoRectParams) -> ColumnElement[bool]:
        if not params.crosses_antimeridian:
            return ST_Intersects(
                Building.location,
                self._envelope(params.min_longitude, params.max_longitude, params),
            )

        return or_(
            ST_Intersects(Building.location, self._envelope(params.min_longitude, 180, params)),
            ST_Intersects(Building.location, self._envelope(-180, params.max_longitude, params)),
        )

    def _envelope(self, xmin, xmax, params: GeoRectParams) -> ColumnElement[bool]:
        return cast(
            ST_SetSRID(ST_MakeEnvelope(xmin, params.min_latitude, xmax, params.max_latitude), 4326),
            _GEOGRAPHY_4326,
        )
