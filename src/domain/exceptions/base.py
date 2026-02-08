class DomainError(Exception):
    """Base domain error."""

    def __init__(self, detail: str = "Domain error"):
        self.detail = detail
        super().__init__(self.detail)
