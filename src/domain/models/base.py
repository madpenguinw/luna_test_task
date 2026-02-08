from sqlalchemy import Column, ForeignKey, Table, Uuid
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""


organization_activity = Table(
    "organization_activity",
    Base.metadata,
    Column(
        "organization_id",
        Uuid,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        Uuid,
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
