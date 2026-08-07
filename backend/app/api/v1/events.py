"""Batched analytics ingest.

The event type is a server-side enum, so an unrecognized type is rejected at validation rather than
polluting the stream. High-frequency interactions are debounced client-side; this endpoint enforces a
batch cap and a per-user rate limit as the backstop.
"""

from __future__ import annotations

from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUser, DbSession
from app.auth.rate_limit import limiter
from app.schemas.learning import EventBatch, EventBatchResult
from app.services.learning_service import LearningService

router = APIRouter(tags=["events"])


@router.post("/events", response_model=EventBatchResult, status_code=status.HTTP_202_ACCEPTED)
async def ingest_events(
    payload: EventBatch, db: DbSession, user: CurrentUser
) -> EventBatchResult:
    limiter.check("events:user", str(user.id), limit=600, window_seconds=60)
    accepted, session_id = await LearningService(db).ingest_events(
        user, payload.events, payload.learning_session_id
    )
    return EventBatchResult(accepted=accepted, learning_session_id=session_id)
