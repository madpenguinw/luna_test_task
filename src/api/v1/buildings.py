from fastapi import APIRouter, Query

from src.api.dependencies import ApiKeyDep, BuildingServiceDep
from src.domain.schemas import BuildingRead, PaginatedResponse

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get(
    "/",
    response_model=PaginatedResponse[BuildingRead],
    summary="List of all buildings",
    description="Returns a paginated list of all buildings in the directory.",
)
async def get_buildings(
    _: ApiKeyDep,
    service: BuildingServiceDep,
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> PaginatedResponse[BuildingRead]:
    return await service.get_all(page=page, size=size)
