from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.domain.exceptions import DomainError, NotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for domain errors."""

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.detail})

    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.detail})

    @app.exception_handler(ValidationError)
    async def validation_error_handler(_: Request, exc: ValidationError) -> JSONResponse:
        errors = exc.errors()
        for error in errors:
            error.pop("ctx", None)
            error.pop("url", None)
        return JSONResponse(status_code=422, content={"detail": jsonable_encoder(errors)})
