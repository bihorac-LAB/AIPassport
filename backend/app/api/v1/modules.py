"""Curriculum reads. Progress is joined in for the authenticated caller only."""

from __future__ import annotations

from fastapi import APIRouter

from app.auth.dependencies import DbSession, OptionalUser
from app.models import ProgressStatus
from app.schemas.learning import (
    ModuleDetail,
    ModulePageDetail,
    ModuleSummary,
    PageProgressOut,
    QuestionOut,
)
from app.services.learning_service import LearningService

router = APIRouter(prefix="/modules", tags=["modules"])


@router.get("", response_model=list[ModuleSummary])
async def list_modules(db: DbSession, user: OptionalUser) -> list[ModuleSummary]:
    service = LearningService(db)
    modules = await service.list_modules()

    completed: set[str] = set()
    if user is not None:
        rows = await service.get_progress_rows(user)
        completed = {r.page_key for r in rows if r.status == ProgressStatus.COMPLETED.value}

    result: list[ModuleSummary] = []
    for module in modules:
        page_keys = [p.key for p in module.pages]
        done = len([k for k in page_keys if k in completed])
        if done == 0:
            status = ProgressStatus.NOT_STARTED
        elif done == len(page_keys):
            status = ProgressStatus.COMPLETED
        else:
            status = ProgressStatus.IN_PROGRESS
        summary = ModuleSummary.model_validate(module)
        summary.pages_completed = done
        summary.pages_total = len(page_keys)
        summary.status = status
        result.append(summary)
    return result


@router.get("/{module_key}", response_model=ModuleDetail)
async def get_module(module_key: str, db: DbSession, user: OptionalUser) -> ModuleDetail:
    service = LearningService(db)
    module = await service.get_module(module_key)

    progress_by_page = {}
    if user is not None:
        rows = await service.get_progress_rows(user)
        progress_by_page = {r.page_key: r for r in rows}

    detail = ModuleDetail.model_validate(module)
    for page_out, page in zip(detail.pages, module.pages, strict=True):
        page_out.questions = [
            QuestionOut.model_validate(q) for q in page.questions if q.is_active
        ]
        row = progress_by_page.get(page.key)
        page_out.progress = PageProgressOut.model_validate(row) if row else None
    return detail


@router.get("/{module_key}/pages/{page_key}", response_model=ModulePageDetail)
async def get_page(
    module_key: str, page_key: str, db: DbSession, user: OptionalUser
) -> ModulePageDetail:
    service = LearningService(db)
    page = await service.get_page(page_key)
    if page.module_key != module_key:
        # Keep URLs honest rather than silently serving a page from another module.
        from app.core.errors import NotFound

        raise NotFound("Page not found in that module.", code="page_not_found")

    detail = ModulePageDetail.model_validate(page)
    detail.questions = [QuestionOut.model_validate(q) for q in page.questions if q.is_active]
    if user is not None:
        row = await service.get_page_progress(user, page.id)
        detail.progress = PageProgressOut.model_validate(row) if row else None
    return detail
