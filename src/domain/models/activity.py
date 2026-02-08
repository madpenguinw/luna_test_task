from __future__ import annotations

from datetime import (
    datetime,  # noqa: TCH003  # needed at runtime by SQLAlchemy Mapped
)
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.models.base import Base, organization_activity

if TYPE_CHECKING:
    from src.domain.models.organization import Organization


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    parent_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    level: Mapped[int] = mapped_column(default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    parent: Mapped[Activity | None] = relationship(
        back_populates="children", remote_side="Activity.id", lazy="joined"
    )
    children: Mapped[list[Activity]] = relationship(
        back_populates="parent", lazy="selectin", cascade="all, delete-orphan"
    )
    organizations: Mapped[list[Organization]] = relationship(
        secondary=organization_activity,
        back_populates="activities",
        lazy="selectin",
    )

    __table_args__ = (CheckConstraint("level >= 1 AND level <= 3", name="ck_activity_level"),)

    def __repr__(self) -> str:
        return f"<Activity(id={self.id}, name='{self.name}', level={self.level})>"
