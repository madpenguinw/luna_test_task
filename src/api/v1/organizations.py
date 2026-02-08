from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import ApiKeyDep, OrganizationServiceDep
from src.domain.schemas import GeoCircleParams, GeoRectParams, OrganizationRead, PaginatedResponse

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get(
    "/by-building/{building_id}",
    response_model=PaginatedResponse[OrganizationRead],
    summary="List organizations in a building",
    description="Returns all organizations located in a specific building.",
    responses={404: {"description": "Building not found"}},
)
async def get_by_building(
    building_id: UUID,
    _: ApiKeyDep,
    service: OrganizationServiceDep,
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> PaginatedResponse[OrganizationRead]:
    return await service.get_by_building(building_id, page=page, size=size)


@router.get(
    "/by-activity/{activity_id}",
    response_model=PaginatedResponse[OrganizationRead],
    summary="List organizations by activity",
    description="Returns organizations that have the specified activity.",
    responses={404: {"description": "Activity not found"}},
)
async def get_by_activity(
    activity_id: UUID,
    _: ApiKeyDep,
    service: OrganizationServiceDep,
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> PaginatedResponse[OrganizationRead]:
    return await service.get_by_activity(activity_id, page=page, size=size)


@router.get(
    "/search/by-activity-tree/{activity_id}",
    response_model=PaginatedResponse[OrganizationRead],
    summary="Search organizations by activity tree",
    description=("Search organizations by activity including all nested child activities. "),
    responses={404: {"description": "Activity not found"}},
)
async def search_by_activity_tree(
    activity_id: UUID,
    _: ApiKeyDep,
    service: OrganizationServiceDep,
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> PaginatedResponse[OrganizationRead]:
    return await service.search_by_activity_tree(activity_id, page=page, size=size)


@router.get(
    "/search/by-name",
    response_model=PaginatedResponse[OrganizationRead],
    summary="Search organizations by name",
    description="Case-insensitive partial name search across all organizations.",
)
async def search_by_name(
    _: ApiKeyDep,
    service: OrganizationServiceDep,
    name: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> PaginatedResponse[OrganizationRead]:
    return await service.search_by_name(name, page=page, size=size)


@router.get(
    "/search/in-radius",
    response_model=PaginatedResponse[OrganizationRead],
    summary="Search organizations within radius",
    description="Find organizations in buildings within a given radius from a geographic point.",
)
async def search_in_radius(
    _: ApiKeyDep,
    service: OrganizationServiceDep,
    params: GeoCircleParams = Depends(),
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> PaginatedResponse[OrganizationRead]:
    return await service.find_in_radius(params, page=page, size=size)


@router.get(
    "/search/in-rect",
    response_model=PaginatedResponse[OrganizationRead],
    summary="Search organizations within rectangle",
    description="Find organizations in buildings within a bounding rectangle.",
)
async def search_in_rect(
    _: ApiKeyDep,
    service: OrganizationServiceDep,
    params: GeoRectParams = Depends(),
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> PaginatedResponse[OrganizationRead]:
    return await service.find_in_rect(params, page=page, size=size)


@router.get(
    "/{organization_id}",
    response_model=OrganizationRead,
    summary="Get organization by ID",
    description=(
        "Returns full information about an organization including its building and activities."
    ),
    responses={404: {"description": "Organization not found"}},
)
async def get_organization(
    organization_id: UUID,
    _: ApiKeyDep,
    service: OrganizationServiceDep,
) -> OrganizationRead:
    return await service.get_by_id(organization_id)
