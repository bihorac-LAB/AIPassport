"""Instructor / admin reads and research export.

Intentionally small: enough structure that a future instructor UI needs no schema change, without
building a CMS now. Every row exported is keyed by the internal UUID only.
"""

from __future__ import annotations

import csv
import io
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select

from app.auth.dependencies import DbSession, require_role
from app.core.errors import NotFound
from app.models import (
    Event,
    PageProgress,
    ProgressStatus,
    Question,
    QuestionResponse,
    User,
    UserRole,
)
from app.schemas.common import ORMModel

router = APIRouter(prefix="/admin", tags=["admin"])

Instructor = Annotated[User, Depends(require_role(UserRole.INSTRUCTOR))]
Admin = Annotated[User, Depends(require_role(UserRole.ADMIN))]


class AdminUserRow(ORMModel):
    id: str
    email: str
    display_name: str
    role: str
    track_pref: str
    is_active: bool
    pages_completed: int


class QuestionDifficulty(ORMModel):
    question_key: str
    module_key: str
    page_key: str
    attempts: int
    correct: int
    accuracy: float | None


class AnalyticsSummary(ORMModel):
    users: int
    active_learners: int
    pages_completed: int
    responses: int
    events: int
    ai_messages: int
    hardest_questions: list[QuestionDifficulty]


@router.get("/users", response_model=list[AdminUserRow])
async def list_users(
    db: DbSession,
    _actor: Instructor,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[AdminUserRow]:
    users = (
        (await db.execute(select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)))
        .scalars()
        .all()
    )
    counts = dict(
        (
            await db.execute(
                select(PageProgress.user_id, func.count())
                .where(PageProgress.status == ProgressStatus.COMPLETED.value)
                .group_by(PageProgress.user_id)
            )
        ).all()
    )
    return [
        AdminUserRow(
            id=str(u.id),
            email=u.email,
            display_name=u.display_name,
            role=u.role,
            track_pref=u.track_pref,
            is_active=u.is_active,
            pages_completed=int(counts.get(u.id, 0)),
        )
        for u in users
    ]


@router.get("/analytics/summary", response_model=AnalyticsSummary)
async def analytics_summary(db: DbSession, _actor: Instructor) -> AnalyticsSummary:
    from app.models import AiMessage

    async def scalar(stmt: Any) -> int:
        return int((await db.execute(stmt)).scalar_one() or 0)

    users = await scalar(select(func.count()).select_from(User))
    active = await scalar(
        select(func.count(func.distinct(PageProgress.user_id))).select_from(PageProgress)
    )
    completed = await scalar(
        select(func.count())
        .select_from(PageProgress)
        .where(PageProgress.status == ProgressStatus.COMPLETED.value)
    )
    responses = await scalar(select(func.count()).select_from(QuestionResponse))
    events = await scalar(select(func.count()).select_from(Event))
    ai_messages = await scalar(select(func.count()).select_from(AiMessage))

    rows = (
        await db.execute(
            select(
                QuestionResponse.question_key,
                QuestionResponse.module_key,
                QuestionResponse.page_key,
                func.count().label("attempts"),
                func.count(func.nullif(QuestionResponse.is_correct, False)).label("correct"),
            )
            .where(QuestionResponse.is_correct.isnot(None))
            .group_by(
                QuestionResponse.question_key,
                QuestionResponse.module_key,
                QuestionResponse.page_key,
            )
            .having(func.count() > 0)
        )
    ).all()

    difficulty = sorted(
        (
            QuestionDifficulty(
                question_key=r.question_key,
                module_key=r.module_key,
                page_key=r.page_key,
                attempts=int(r.attempts),
                correct=int(r.correct),
                accuracy=(int(r.correct) / int(r.attempts)) if r.attempts else None,
            )
            for r in rows
        ),
        key=lambda d: (d.accuracy if d.accuracy is not None else 1.0),
    )[:10]

    return AnalyticsSummary(
        users=users,
        active_learners=active,
        pages_completed=completed,
        responses=responses,
        events=events,
        ai_messages=ai_messages,
        hardest_questions=difficulty,
    )


_EXPORTS: dict[str, tuple[Any, list[str]]] = {
    "responses": (
        QuestionResponse,
        [
            "id",
            "user_id",
            "question_key",
            "question_version",
            "module_key",
            "page_key",
            "learning_session_id",
            "attempt_no",
            "answer",
            "is_final",
            "is_correct",
            "score",
            "response_time_ms",
            "created_at",
        ],
    ),
    "events": (
        Event,
        [
            "id",
            "user_id",
            "learning_session_id",
            "event_type",
            "module_key",
            "page_key",
            "activity_key",
            "question_key",
            "section_id",
            "event_metadata",
            "client_ts",
            "created_at",
        ],
    ),
    "progress": (
        PageProgress,
        [
            "id",
            "user_id",
            "module_key",
            "page_key",
            "status",
            "sections_completed",
            "seconds_spent",
            "visit_count",
            "started_at",
            "completed_at",
            "updated_at",
        ],
    ),
}


@router.get("/export/{dataset}.csv")
async def export_dataset(
    dataset: Literal["responses", "events", "progress"],
    db: DbSession,
    _actor: Instructor,
    limit: int = Query(default=10000, ge=1, le=100000),
) -> StreamingResponse:
    """Pseudonymized export: user_id UUIDs only, never email or display name."""
    entry = _EXPORTS.get(dataset)
    if entry is None:  # pragma: no cover - Literal already constrains this
        raise NotFound("Unknown dataset.", code="unknown_dataset")
    model, columns = entry

    rows = (
        (await db.execute(select(model).order_by(model.created_at.desc()).limit(limit)))
        .scalars()
        .all()
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(columns)
    for row in rows:
        writer.writerow([getattr(row, col, "") for col in columns])
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="aipassport_{dataset}.csv"'},
    )


class QuestionAdminRow(ORMModel):
    key: str
    module_key: str
    page_key: str
    type: str
    prompt: str
    version: int
    is_graded: bool
    is_active: bool


@router.get("/questions", response_model=list[QuestionAdminRow])
async def list_questions(db: DbSession, _actor: Instructor) -> list[QuestionAdminRow]:
    rows = (
        (await db.execute(select(Question).order_by(Question.key)))
        .scalars()
        .all()
    )
    return [QuestionAdminRow.model_validate(r) for r in rows]
