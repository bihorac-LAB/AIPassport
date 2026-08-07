"""Progress and learning sessions."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUser, DbSession
from app.auth.rate_limit import limiter
from app.schemas.common import MessageResponse
from app.schemas.learning import (
    LearningSessionOut,
    LearningSessionStart,
    PageProgressOut,
    ProgressOverview,
    ProgressUpdate,
    ResumePointer,
)
from app.services.learning_service import LearningService

router = APIRouter(tags=["progress"])


@router.post(
    "/sessions",
    response_model=LearningSessionOut,
    status_code=status.HTTP_201_CREATED,
)
async def start_session(
    payload: LearningSessionStart, db: DbSession, user: CurrentUser
) -> LearningSessionOut:
    limiter.check("session_start:user", str(user.id), limit=60, window_seconds=3600)
    session = await LearningService(db).start_learning_session(
        user,
        is_embedded=payload.is_embedded,
        client_meta={
            "timezone": payload.timezone,
            "viewport_width": payload.viewport_width,
            "referrer_kind": payload.referrer_kind,
        },
    )
    return LearningSessionOut.model_validate(session)


@router.post("/sessions/{session_id}/end", response_model=MessageResponse)
async def end_session(
    session_id: uuid.UUID, db: DbSession, user: CurrentUser
) -> MessageResponse:
    service = LearningService(db)
    await service.end_learning_session(user, session_id)
    await db.commit()
    return MessageResponse(detail="Session closed.")


@router.get("/progress/me", response_model=ProgressOverview)
async def my_progress(db: DbSession, user: CurrentUser) -> ProgressOverview:
    service = LearningService(db)
    rows = await service.get_progress_rows(user)
    resume = await service.resume_pointer(user)
    return ProgressOverview(
        pages=[PageProgressOut.model_validate(r) for r in rows],
        modules_completed=await service.completed_modules(user),
        total_seconds=sum(r.seconds_spent for r in rows),
        resume=ResumePointer(module_key=resume[0], page_key=resume[1], section_id=resume[2])
        if resume
        else None,
    )


@router.post("/progress/pages/{page_key}", response_model=PageProgressOut)
async def update_page_progress(
    page_key: str, payload: ProgressUpdate, db: DbSession, user: CurrentUser
) -> PageProgressOut:
    limiter.check("progress:user", str(user.id), limit=600, window_seconds=3600)
    service = LearningService(db)
    page = await service.get_page(page_key)
    row = await service.upsert_progress(user, page, payload)
    return PageProgressOut.model_validate(row)
