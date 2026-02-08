from typing import Annotated

from fastapi import Header, HTTPException, status

from src.core.config import config


async def verify_api_key(
    x_api_key: Annotated[str, Header(description="Static API key for authentication")],
) -> str:
    if x_api_key != config.security.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return x_api_key
