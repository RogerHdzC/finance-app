from __future__ import annotations
import logging
from typing import Any, Dict
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from contextlib import asynccontextmanager

from app.core.config import validate_settings

from app.exceptions.base import (
    DomainError,
    BadRequestError,
    NotFoundError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
    InternalServerError,
    ValidationError
)

from app.routers import user, auth

logger = logging.getLogger("finance_api")

def make_error(
    *,
    code: str,
    message: str,
    trace_id: str,
    details: Any | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "details": details,
        "trace_id": trace_id,
    }

def status_for_domain_error(exc: DomainError) -> int:
    if isinstance(exc, ValidationError):
        return 422
    if isinstance(exc, BadRequestError):
        return 400
    if isinstance(exc, UnauthorizedError):
        return 401
    if isinstance(exc, ForbiddenError):
        return 403
    if isinstance(exc, NotFoundError):
        return 404
    if isinstance(exc, ConflictError):
        return 409
    if isinstance(exc, InternalServerError):
        return 500
    return 400

def create_app() -> FastAPI:
    
    app = FastAPI(
        title="Finance API",
        version="0.2.0",
        description="API for managing finance-related operations.",
    )
    # app.include_router(category.router, prefix="/api/v1")
    app.include_router(user.router, prefix="/api/v1")
    app.include_router(auth.router, prefix="/api/v1")

    @app.middleware("http")
    async def add_trace_id(request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id") or uuid.uuid4().hex
        request.state.trace_id = trace_id
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        return response
    
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        trace_id = getattr(request.state, "trace_id", uuid.uuid4().hex)
        status_code = status_for_domain_error(exc)

        logger.info(
            "DomainError: %s %s -> %s (%s) trace_id=%s",
            request.method,
            request.url.path,
            status_code,
            exc.code,
            trace_id,
        )

        return JSONResponse(
            status_code=status_code,
            content=make_error(
                code=exc.code,
                message=exc.detail,
                details=exc.meta,
                trace_id=trace_id,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        trace_id = getattr(request.state, "trace_id", uuid.uuid4().hex)

        # FastAPI gives locations like: ("body","field") or ("query","limit")
        errors = []
        for e in exc.errors():
            loc = e.get("loc", [])
            field = ".".join(str(x) for x in loc[1:]) if len(loc) > 1 else ".".join(str(x) for x in loc)
            errors.append({"field": field or "body", "reason": e.get("msg", "Invalid value")})

        return JSONResponse(
            status_code=422,
            content=make_error(
                code="VALIDATION_ERROR",
                message="Validation failed.",
                details={"errors": errors},
                trace_id=trace_id,
            ),
        )
  
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        trace_id = getattr(request.state, "trace_id", uuid.uuid4().hex)
        logger.warning("IntegrityError: %s %s trace_id=%s", request.method, request.url.path, trace_id, exc_info=True)

        return JSONResponse(
            status_code=409,
            content=make_error(
                code="database_integrity_error",
                message="Database constraint violation.",
                details=None,
                trace_id=trace_id,
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        trace_id = getattr(request.state, "trace_id", uuid.uuid4().hex)
        logger.error("Unhandled exception: %s %s trace_id=%s", request.method, request.url.path, trace_id, exc_info=True)

        return JSONResponse(
            status_code=500,
            content=make_error(
                code="INTERNAL_ERROR",
                message="Unexpected error.",
                details=None,
                trace_id=trace_id,
            ),
        )

    return app

app = create_app()