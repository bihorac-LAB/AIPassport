"""Liveness and readiness."""

from __future__ import annotations

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.auth.dependencies import DbSession
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.common import ORMModel
from app.services.content_registry import content_registry
from app.services.llm import build_provider

router = APIRouter(tags=["health"])
log = get_logger("aipassport.health")


class HealthResponse(ORMModel):
    status: str
    environment: str


class ReadyCheck(ORMModel):
    name: str
    ok: bool
    detail: str | None = None


class ReadyResponse(ORMModel):
    status: str
    checks: list[ReadyCheck]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", environment=settings.ENVIRONMENT)


@router.get("/health/ready", response_model=ReadyResponse)
async def ready(db: DbSession, response: Response) -> ReadyResponse:
    checks: list[ReadyCheck] = []

    try:
        await db.execute(text("select 1"))
        checks.append(ReadyCheck(name="database", ok=True))
    except Exception as exc:  # noqa: BLE001 - readiness must report, not raise
        log.error("readiness_database_failed", error=type(exc).__name__)
        checks.append(ReadyCheck(name="database", ok=False, detail="unreachable"))

    try:
        version = (
            await db.execute(text("select version_num from alembic_version limit 1"))
        ).scalar_one_or_none()
        checks.append(
            ReadyCheck(
                name="migrations",
                ok=version is not None,
                detail=version or "alembic_version is empty",
            )
        )
    except Exception:  # noqa: BLE001
        checks.append(
            ReadyCheck(name="migrations", ok=False, detail="alembic_version table missing")
        )

    try:
        module_count = (
            await db.execute(text("select count(*) from modules"))
        ).scalar_one()
        checks.append(
            ReadyCheck(
                name="content",
                ok=int(module_count or 0) > 0,
                detail=f"{int(module_count or 0)} modules seeded",
            )
        )
    except Exception:  # noqa: BLE001
        checks.append(ReadyCheck(name="content", ok=False, detail="modules table missing"))

    problems = content_registry.validate()
    checks.append(
        ReadyCheck(
            name="content_manifest",
            ok=not problems,
            detail="; ".join(problems[:3]) if problems else "valid",
        )
    )

    provider = build_provider()
    checks.append(
        ReadyCheck(
            name="llm",
            ok=True,
            detail=f"provider={provider.name}"
            + (" (offline stub — no credential configured)" if provider.name == "echo" else ""),
        )
    )

    # The LLM provider is optional, so it never fails readiness.
    critical_ok = all(c.ok for c in checks if c.name != "llm")
    if not critical_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadyResponse(status="ready" if critical_ok else "degraded", checks=checks)
