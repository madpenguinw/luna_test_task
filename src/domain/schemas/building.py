from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BuildingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(examples=["550e8400-e29b-41d4-a716-446655440000"])
    address: str = Field(examples=["г. Санкт-Петербург, Невский проспект, 28"])
    latitude: float = Field(ge=-90, le=90, examples=[59.935800])
    longitude: float = Field(ge=-180, le=180, examples=[30.325875])
    created_at: datetime
