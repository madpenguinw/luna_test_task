from __future__ import annotations

from datetime import datetime  # noqa: TCH003 - needed at runtime by SQLAlchemy Mapped
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.models.base import Base, organization_activity

if TYPE_CHECKING:
    from src.domain.models.activity import Activity
    from src.domain.models.building import Building


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    phone_numbers: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)), nullable=False, default=list
    )
    building_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("buildings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    building: Mapped[Building] = relationship(back_populates="organizations", lazy="joined")
    activities: Mapped[list[Activity]] = relationship(
        secondary=organization_activity,
        back_populates="organizations",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}')>"
