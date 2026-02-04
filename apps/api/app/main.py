from __future__ import annotations
import logging
from typing import Any, Dict
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from sqlalchemy.exc import IntegrityError

from app.exceptions.base import (
    DomainError,
    BadRequestError,
    NotFoundError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
    InternalServerError,
)

from app.routers import user

logger = logging.getLogger("finance_api")

def make_error_payload(
    *,
    code: str,
    detail: str,
    meta: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"code": code, "detail": detail}
    if meta:
        payload["meta"] = meta
    return payload

def create_app() -> FastAPI:
    app = FastAPI(
        title="Finance API",
        version="0.1.0",
        description="API for managing finance-related operations.",
    )
    # app.include_router(category.router, prefix="/api/v1")
    app.include_router(user.router, prefix="/api/v1")
    
    @app.exception_handler(DomainError)
    async def domain_error_handler(
        request: Request,
        exc: DomainError
    ) -> JSONResponse:
        logger.error(f"Domain error: {exc}")
        status_code = 400
        if isinstance(exc, BadRequestError):
            status_code = 400
        elif isinstance(exc, NotFoundError):
            status_code = 404
        elif isinstance(exc, ConflictError):
            status_code = 409
        elif isinstance(exc, UnauthorizedError):
            status_code = 401
        elif isinstance(exc, ForbiddenError):
            status_code = 403
        elif isinstance(exc, InternalServerError):
            status_code = 500
        
        logger.info(
            "DomainError: %s %s -> %s (%s)",
            request.method,
            request.url.path,
            status_code,
            exc.code,
        )
        return JSONResponse(status_code=status_code,
                            content=make_error_payload(
                                code=exc.code,
                                detail=exc.detail,
                                meta=exc.meta))
    
    @app.exception_handler(RequestValidationError)
    async def response_validation_handler(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        logger.error(
                     "Response validation error: %s %s",
                     request.method,
                     request.url.path,
                     exc_info=True,
                     )
        
        return JSONResponse(
            status_code=422,
            content=make_error_payload(
                code="validation_error",
                detail="Request validation failed.",
                )
        )
        
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request,
        exc: IntegrityError
    ) -> JSONResponse:
        logger.warning(
                     "Database integrity error: %s %s",
                     request.method,
                     request.url.path,
                     exc_info=True,
                     )
        
        return JSONResponse(
            status_code=409,
            content=make_error_payload(
                code="database_integrity_error",
                detail="Database constraint violation.",
                )
        )
        
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        logger.error(
                     "Unhandled exception: %s %s",
                     request.method,
                     request.url.path,
                     exc_info=True,
                     )
        
        return JSONResponse(
            status_code=500,
            content=make_error_payload(
                code="internal_server_error",
                detail="An internal server error occurred.",
                )
        )
    return app

app = create_app()