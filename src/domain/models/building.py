from __future__ import annotations

from datetime import (
    datetime,  # noqa: TCH003 - needed at runtime by SQLAlchemy Mapped
)
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from geoalchemy2 import Geography, WKBElement
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point
from sqlalchemy import DateTime, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.models.base import Base

if TYPE_CHECKING:
    from src.domain.models.organization import Organization


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[WKBElement] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organizations: Mapped[list[Organization]] = relationship(
        back_populates="building", lazy="selectin"
    )

    __table_args__ = (Index("ix_buildings_location", "location", postgresql_using="gist"),)

    @property
    def latitude(self) -> float:
        point = to_shape(self.location)
        return point.y

    @property
    def longitude(self) -> float:
        point = to_shape(self.location)
        return point.x

    @classmethod
    def make_location(cls, latitude: float, longitude: float) -> WKBElement:
        return from_shape(Point(longitude, latitude), srid=4326)

    def __repr__(self) -> str:
        return f"<Building(id={self.id}, address='{self.address}')>"
