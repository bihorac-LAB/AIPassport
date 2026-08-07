"""Application error hierarchy and exception handlers.

Clients receive ``{"detail": str, "code": str}`` and never a stack trace.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

log = get_logger("aipassport.error")


class APIError(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "bad_request"
    detail: str = "Request could not be processed."

    def __init__(
        self,
        detail: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        self.detail = detail or self.detail
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.headers = headers or {}
        self.extra = extra or {}
        super().__init__(self.detail)

    def to_response(self) -> JSONResponse:
        payload: dict[str, Any] = {"detail": self.detail, "code": self.code}
        payload.update(self.extra)
        return JSONResponse(payload, status_code=self.status_code, headers=self.headers)


class BadRequest(APIError):
    pass


class Unauthorized(APIError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"
    detail = "Authentication required."


class InvalidCredentials(Unauthorized):
    code = "invalid_credentials"
    detail = "Email or password is incorrect."


class Forbidden(APIError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "forbidden"
    detail = "You do not have access to this resource."


class NotFound(APIError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"
    detail = "Resource not found."


class Conflict(APIError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"
    detail = "Resource conflict."


class EmailAlreadyRegistered(Conflict):
    code = "email_registered"
    detail = "An account with that email already exists."


class RateLimited(APIError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = "rate_limited"
    detail = "Too many requests. Please try again shortly."


class ServiceUnavailable(APIError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "service_unavailable"
    detail = "A dependency is temporarily unavailable."


class ModelUnavailable(ServiceUnavailable):
    code = "model_unavailable"
    detail = "The AI assistant is temporarily unavailable. Please try again in a moment."


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def _api_error(_request: Request, exc: APIError) -> JSONResponse:
        if exc.status_code >= 500:
            log.error("api_error", code=exc.code, detail=exc.detail, status=exc.status_code)
        else:
            log.info("api_error", code=exc.code, status=exc.status_code)
        return exc.to_response()

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
        fields = [
            {
                "field": ".".join(str(p) for p in err.get("loc", ()) if p != "body"),
                "message": err.get("msg", "invalid"),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            {"detail": "Request validation failed.", "code": "validation_error", "fields": fields},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = {401: "unauthorized", 403: "forbidden", 404: "not_found", 405: "method_not_allowed"}.get(
            exc.status_code, "http_error"
        )
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed."
        return JSONResponse({"detail": detail, "code": code}, status_code=exc.status_code)

    @app.exception_handler(IntegrityError)
    async def _integrity_error(_request: Request, exc: IntegrityError) -> JSONResponse:
        log.warning("db_integrity_error", error=str(exc.orig)[:300])
        return JSONResponse(
            {"detail": "That operation conflicts with existing data.", "code": "conflict"},
            status_code=status.HTTP_409_CONFLICT,
        )

    @app.exception_handler(SQLAlchemyError)
    async def _db_error(_request: Request, exc: SQLAlchemyError) -> JSONResponse:
        log.error("db_error", error=type(exc).__name__)
        return JSONResponse(
            {"detail": "A database error occurred.", "code": "database_error"},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    @app.exception_handler(Exception)
    async def _unhandled(_request: Request, exc: Exception) -> JSONResponse:
        log.exception("unhandled_exception", error=type(exc).__name__)
        return JSONResponse(
            {"detail": "An unexpected error occurred.", "code": "internal_error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
