import math
from collections.abc import Sequence

from pydantic import BaseModel

from src.domain.schemas.pagination import PaginatedResponse


def paginate(
    items: Sequence,
    total: int,
    page: int,
    size: int,
    schema: type[BaseModel],
) -> PaginatedResponse:
    pages = math.ceil(total / size) if size > 0 else 0
    return PaginatedResponse(
        items=[schema.model_validate(item) for item in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )
