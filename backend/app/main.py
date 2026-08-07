"""FastAPI application factory."""

from __future__ import annotations

import time
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1 import api_router, health
from app.core.config import settings
from app.core.db import dispose_engine
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.services.content_registry import content_registry

log = get_logger("aipassport.app")

MAX_BODY_BYTES = 1_048_576  # 1MB; the reverse proxy enforces the same cap in production.


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    problems = content_registry.validate()
    if problems:
        log.warning("content_manifest_problems", problems=problems[:5])
    log.info(
        "startup",
        environment=settings.ENVIRONMENT,
        modules=len(content_registry.modules),
        docs=settings.docs_enabled,
    )
    yield
    await dispose_engine()
    log.info("shutdown")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Per-request id, structured access log, and a body-size guard."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:16]
        structlog.contextvars.bind_contextvars(request_id=request_id)

        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > MAX_BODY_BYTES:
            structlog.contextvars.clear_contextvars()
            return Response(
                content='{"detail":"Request body is too large.","code":"payload_too_large"}',
                status_code=413,
                media_type="application/json",
            )

        started = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            duration_ms = int((time.perf_counter() - started) * 1000)

        response.headers["x-request-id"] = request_id
        if request.url.path not in ("/api/v1/health", "/health"):
            log.info(
                "request",
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                duration_ms=duration_ms,
            )
        structlog.contextvars.clear_contextvars()
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Defence in depth; the reverse proxy sets these too."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-Frame-Options", "DENY")
        if settings.is_production:
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return response


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description=(
            "Backend for AIPassport — an interactive biomedical AI learning platform. "
            "All learner writes are attributed to the authenticated user; no endpoint accepts a "
            "client-supplied user id."
        ),
        lifespan=lifespan,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=1024)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-CSRF-Token", "X-Request-Id"],
        expose_headers=["X-Request-Id", "Retry-After"],
        max_age=600,
    )

    register_exception_handlers(app)

    app.include_router(health.router, prefix=settings.API_V1_PREFIX)
    # Unprefixed alias so a load balancer health check does not need to know the API version.
    app.include_router(health.router)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
