from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.domain.schemas.activity import ActivityRead
from src.domain.schemas.building import BuildingRead


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(examples=["550e8400-e29b-41d4-a716-446655440000"])
    name: str = Field(examples=['ООО "Рога и Копыта"'])
    phone_numbers: list[str] = Field(examples=[["2-222-222", "3-333-333", "8-951-666-66-66"]])
    building: BuildingRead
    activities: list[ActivityRead]
    created_at: datetime
