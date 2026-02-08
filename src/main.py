from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.middleware import register_exception_handlers
from src.api.v1.router import api_v1_router
from src.core.config import config


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup and shutdown events."""
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=config.app.title,
        version=config.app.version,
        description=(
            "REST API for Organization Directory. "
            "Provides search and management of organizations, buildings, and activities."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    register_exception_handlers(app)
    app.include_router(api_v1_router)

    @app.get("/health", tags=["Health"], include_in_schema=False)
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
