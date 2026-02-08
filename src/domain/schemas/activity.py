from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel, ConfigDict, Field


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(examples=["550e8400-e29b-41d4-a716-446655440000"])
    name: str = Field(examples=["Еда"])
    parent_id: UUID | None = Field(examples=[None])
    level: int
    created_at: datetime
