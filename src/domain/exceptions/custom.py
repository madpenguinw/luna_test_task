from uuid import UUID

from src.domain.exceptions.base import DomainError


class NotFoundError(DomainError):
    """Entity not found."""

    def __init__(self, entity: str, entity_id: UUID | str):
        super().__init__(f"{entity} with id={entity_id} not found")
