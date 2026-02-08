from typing import Annotated

from fastapi import Depends

from src.api.dependencies.database import SessionDep
from src.infrastructure.repositories.activity import ActivityRepository
from src.infrastructure.repositories.building import BuildingRepository
from src.infrastructure.repositories.organization import OrganizationRepository
from src.services.building import BuildingService
from src.services.organization import OrganizationService


def get_organization_service(session: SessionDep) -> OrganizationService:
    return OrganizationService(
        organization_repo=OrganizationRepository(session),
        building_repo=BuildingRepository(session),
        activity_repo=ActivityRepository(session),
    )


def get_building_service(session: SessionDep) -> BuildingService:
    return BuildingService(repository=BuildingRepository(session))


OrganizationServiceDep = Annotated[OrganizationService, Depends(get_organization_service)]
BuildingServiceDep = Annotated[BuildingService, Depends(get_building_service)]
