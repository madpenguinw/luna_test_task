from src.domain.interfaces.repositories import BuildingRepositoryProtocol
from src.domain.schemas.building import BuildingRead
from src.domain.schemas.pagination import PaginatedResponse
from src.services.pagination import paginate


class BuildingService:
    def __init__(self, repository: BuildingRepositoryProtocol) -> None:
        self._repo = repository

    async def get_all(self, *, page: int = 1, size: int = 20) -> PaginatedResponse[BuildingRead]:
        offset = (page - 1) * size
        items = await self._repo.get_all(offset=offset, limit=size)
        total = await self._repo.count()
        return paginate(items, total, page, size, BuildingRead)
