"""Question responses and structured activity results.

Note the absence of any ``user_id`` parameter: the owning user is resolved from the access token.
"""

from __future__ import annotations

from fastapi import APIRouter, Query, status

from app.auth.dependencies import CurrentUser, DbSession
from app.auth.rate_limit import limiter
from app.schemas.learning import (
    ActivityResultCreate,
    ActivityResultOut,
    QuestionOut,
    ResponseCreate,
    ResponseOut,
    ResponseResult,
)
from app.services.learning_service import LearningService

router = APIRouter(tags=["responses"])


@router.post("/responses", response_model=ResponseResult, status_code=status.HTTP_201_CREATED)
async def submit_response(
    payload: ResponseCreate, db: DbSession, user: CurrentUser
) -> ResponseResult:
    limiter.check("responses:user", str(user.id), limit=300, window_seconds=60)
    record, graded, _created = await LearningService(db).submit_response(user, payload)
    return ResponseResult(
        response=ResponseOut.model_validate(record),
        feedback=graded.feedback,
        explanation=graded.explanation,
        correct_answer=graded.correct_answer,
    )


@router.get("/responses/me", response_model=list[ResponseOut])
async def my_responses(
    db: DbSession,
    user: CurrentUser,
    page_key: str | None = Query(default=None, max_length=64),
    module_key: str | None = Query(default=None, max_length=64),
) -> list[ResponseOut]:
    rows = await LearningService(db).latest_responses(
        user, page_key=page_key, module_key=module_key
    )
    return [ResponseOut.model_validate(r) for r in rows]


@router.get("/responses/me/{question_key}/history", response_model=list[ResponseOut])
async def my_response_history(
    question_key: str, db: DbSession, user: CurrentUser
) -> list[ResponseOut]:
    rows = await LearningService(db).response_history(user, question_key)
    return [ResponseOut.model_validate(r) for r in rows]


@router.get("/questions/{question_key}", response_model=QuestionOut)
async def get_question(question_key: str, db: DbSession) -> QuestionOut:
    question = await LearningService(db).get_question(question_key)
    return QuestionOut.model_validate(question)


@router.post(
    "/activity-results", response_model=ActivityResultOut, status_code=status.HTTP_201_CREATED
)
async def save_activity_result(
    payload: ActivityResultCreate, db: DbSession, user: CurrentUser
) -> ActivityResultOut:
    limiter.check("activity_results:user", str(user.id), limit=200, window_seconds=60)
    record, _created = await LearningService(db).save_activity_result(user, payload)
    return ActivityResultOut.model_validate(record)


@router.get("/activity-results/me", response_model=list[ActivityResultOut])
async def my_activity_results(
    db: DbSession,
    user: CurrentUser,
    page_key: str | None = Query(default=None, max_length=64),
) -> list[ActivityResultOut]:
    rows = await LearningService(db).latest_activity_results(user, page_key=page_key)
    return [ActivityResultOut.model_validate(r) for r in rows]
