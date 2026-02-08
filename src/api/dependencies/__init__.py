from typing import Annotated

from fastapi import Depends

from src.api.dependencies.auth import verify_api_key
from src.api.dependencies.database import SessionDep
from src.api.dependencies.services import (
    BuildingServiceDep,
    OrganizationServiceDep,
)

ApiKeyDep = Annotated[str, Depends(verify_api_key)]

__all__ = [
    "ApiKeyDep",
    "BuildingServiceDep",
    "OrganizationServiceDep",
    "SessionDep",
]
