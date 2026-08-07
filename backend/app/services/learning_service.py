"""Curriculum reads, progress, responses, activity results, events, and learning sessions."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import Select, func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.errors import Conflict, NotFound
from app.core.logging import get_logger
from app.models import (
    ActivityResult,
    Event,
    LearningSession,
    Module,
    ModulePage,
    PageProgress,
    ProgressStatus,
    Question,
    QuestionResponse,
    User,
)
from app.schemas.learning import (
    ActivityResultCreate,
    EventIn,
    ProgressUpdate,
    ResponseCreate,
)
from app.services.grading import Graded, grade

log = get_logger("aipassport.learning")


def _stable_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode()
    ).hexdigest()


class LearningService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Curriculum ──────────────────────────────────────────────────────────

    def _module_query(self) -> Select[tuple[Module]]:
        return (
            select(Module)
            .where(Module.is_published.is_(True))
            .options(selectinload(Module.pages))
            .order_by(Module.position)
        )

    async def list_modules(self) -> list[Module]:
        return list((await self.db.execute(self._module_query())).scalars().all())

    async def get_module(self, module_key: str) -> Module:
        stmt = (
            select(Module)
            .where(Module.key == module_key)
            .options(selectinload(Module.pages).selectinload(ModulePage.questions))
        )
        module = (await self.db.execute(stmt)).scalar_one_or_none()
        if module is None:
            raise NotFound("Module not found.", code="module_not_found")
        return module

    async def get_page(self, page_key: str) -> ModulePage:
        stmt = (
            select(ModulePage)
            .where(ModulePage.key == page_key)
            .options(selectinload(ModulePage.questions))
        )
        page = (await self.db.execute(stmt)).scalar_one_or_none()
        if page is None:
            raise NotFound("Page not found.", code="page_not_found")
        return page

    async def get_question(self, question_key: str) -> Question:
        stmt = select(Question).where(Question.key == question_key, Question.is_active.is_(True))
        question = (await self.db.execute(stmt)).scalar_one_or_none()
        if question is None:
            raise NotFound("Question not found.", code="question_not_found")
        return question

    # ── Learning sessions ───────────────────────────────────────────────────

    async def start_learning_session(
        self, user: User, *, is_embedded: bool, client_meta: dict[str, Any]
    ) -> LearningSession:
        session = LearningSession(
            user_id=user.id, is_embedded=is_embedded, client_meta=client_meta
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def touch_learning_session(
        self, user: User, session_id: uuid.UUID | None
    ) -> LearningSession | None:
        if session_id is None:
            return None
        session = await self.db.get(LearningSession, session_id)
        if session is None or session.user_id != user.id:
            return None
        now = datetime.now(UTC)
        idle_cutoff = now - timedelta(minutes=settings.LEARNING_SESSION_IDLE_MINUTES)
        if session.ended_at is None and session.last_seen_at < idle_cutoff:
            # Close the stale sitting lazily rather than with a background job.
            session.ended_at = session.last_seen_at
        session.last_seen_at = now
        return session

    async def end_learning_session(self, user: User, session_id: uuid.UUID) -> None:
        session = await self.db.get(LearningSession, session_id)
        if session is None or session.user_id != user.id or session.ended_at is not None:
            return
        session.ended_at = datetime.now(UTC)

    # ── Progress ────────────────────────────────────────────────────────────

    async def get_progress_rows(self, user: User) -> list[PageProgress]:
        stmt = (
            select(PageProgress)
            .where(PageProgress.user_id == user.id)
            .order_by(PageProgress.module_key, PageProgress.page_key)
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_page_progress(self, user: User, page_id: uuid.UUID) -> PageProgress | None:
        stmt = select(PageProgress).where(
            PageProgress.user_id == user.id, PageProgress.page_id == page_id
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def upsert_progress(
        self, user: User, page: ModulePage, payload: ProgressUpdate
    ) -> PageProgress:
        row = await self.get_page_progress(user, page.id)
        if row is None:
            row = PageProgress(
                user_id=user.id,
                page_id=page.id,
                module_key=page.module_key,
                page_key=page.key,
                status=ProgressStatus.IN_PROGRESS.value,
                sections_completed=[],
                visit_count=0,
            )
            self.db.add(row)
            await self.db.flush()

        if payload.register_visit:
            row.visit_count += 1

        if payload.seconds_delta:
            row.seconds_spent += min(payload.seconds_delta, settings.MAX_TIME_DELTA_SECONDS)

        if payload.last_section_id:
            row.last_section_id = payload.last_section_id

        if payload.section_completed:
            completed = list(row.sections_completed or [])
            if payload.section_completed not in completed:
                completed.append(payload.section_completed)
                row.sections_completed = completed

        required = set(page.required_sections or [])
        done = set(row.sections_completed or [])
        should_complete = payload.status == "completed" or (bool(required) and required <= done)

        if should_complete and row.status != ProgressStatus.COMPLETED.value:
            row.status = ProgressStatus.COMPLETED.value
            row.completed_at = datetime.now(UTC)
        elif not should_complete and row.status == ProgressStatus.NOT_STARTED.value:
            row.status = ProgressStatus.IN_PROGRESS.value

        await self.touch_learning_session(user, payload.learning_session_id)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def completed_modules(self, user: User) -> list[str]:
        """A module is complete when both of its pages are complete. Derived, never stored."""
        modules = await self.list_modules()
        rows = await self.get_progress_rows(user)
        completed_pages = {
            r.page_key for r in rows if r.status == ProgressStatus.COMPLETED.value
        }
        result: list[str] = []
        for module in modules:
            page_keys = {p.key for p in module.pages}
            if page_keys and page_keys <= completed_pages:
                result.append(module.key)
        return result

    async def resume_pointer(self, user: User) -> tuple[str, str, str | None] | None:
        stmt = (
            select(PageProgress)
            .where(PageProgress.user_id == user.id)
            .order_by(PageProgress.updated_at.desc())
            .limit(1)
        )
        row = (await self.db.execute(stmt)).scalar_one_or_none()
        if row is None:
            return None
        return row.module_key, row.page_key, row.last_section_id

    # ── Question responses (append-only) ────────────────────────────────────

    async def submit_response(
        self, user: User, payload: ResponseCreate
    ) -> tuple[QuestionResponse, Graded, bool]:
        question = await self.get_question(payload.question_key)
        graded = grade(question, payload.answer)

        idempotency_key = payload.idempotency_key or _stable_hash(
            [str(user.id), question.key, graded.answer, payload.is_final]
        )

        # Scoped to this user: another learner's identical answer must not block theirs.
        existing = (
            await self.db.execute(
                select(QuestionResponse).where(
                    QuestionResponse.user_id == user.id,
                    QuestionResponse.idempotency_key == idempotency_key,
                )
            )
        ).scalar_one_or_none()
        if existing is not None:
            if existing.answer != graded.answer:
                raise Conflict(
                    "That idempotency key was used with a different answer.",
                    code="idempotency_conflict",
                )
            return existing, graded, False

        max_attempt = (
            await self.db.execute(
                select(func.coalesce(func.max(QuestionResponse.attempt_no), 0)).where(
                    QuestionResponse.user_id == user.id,
                    QuestionResponse.question_id == question.id,
                )
            )
        ).scalar_one()

        if payload.is_final:
            # Previous attempts are preserved; only the "latest" marker moves.
            await self.db.execute(
                update(QuestionResponse)
                .where(
                    QuestionResponse.user_id == user.id,
                    QuestionResponse.question_id == question.id,
                    QuestionResponse.is_final.is_(True),
                )
                .values(is_final=False)
            )

        session = await self.touch_learning_session(user, payload.learning_session_id)
        record = QuestionResponse(
            user_id=user.id,  # always from the token, never from the request body
            question_id=question.id,
            question_key=question.key,
            question_version=question.version,
            module_key=question.module_key,
            page_key=question.page_key,
            learning_session_id=session.id if session else None,
            attempt_no=int(max_attempt) + 1,
            answer=graded.answer,
            is_final=payload.is_final,
            is_correct=graded.is_correct,
            score=graded.score,
            response_time_ms=payload.response_time_ms,
            client_submitted_at=payload.client_submitted_at,
            idempotency_key=idempotency_key,
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record, graded, True

    async def latest_responses(
        self, user: User, *, page_key: str | None = None, module_key: str | None = None
    ) -> list[QuestionResponse]:
        stmt = select(QuestionResponse).where(
            QuestionResponse.user_id == user.id, QuestionResponse.is_final.is_(True)
        )
        if page_key:
            stmt = stmt.where(QuestionResponse.page_key == page_key)
        if module_key:
            stmt = stmt.where(QuestionResponse.module_key == module_key)
        stmt = stmt.order_by(QuestionResponse.question_key)
        return list((await self.db.execute(stmt)).scalars().all())

    async def response_history(self, user: User, question_key: str) -> list[QuestionResponse]:
        stmt = (
            select(QuestionResponse)
            .where(
                QuestionResponse.user_id == user.id,
                QuestionResponse.question_key == question_key,
            )
            .order_by(QuestionResponse.attempt_no)
        )
        return list((await self.db.execute(stmt)).scalars().all())

    # ── Activity results ────────────────────────────────────────────────────

    async def save_activity_result(
        self, user: User, payload: ActivityResultCreate
    ) -> tuple[ActivityResult, bool]:
        idempotency_key = payload.idempotency_key or _stable_hash(
            [str(user.id), payload.activity_key, payload.payload]
        )
        existing = (
            await self.db.execute(
                select(ActivityResult).where(
                    ActivityResult.user_id == user.id,
                    ActivityResult.idempotency_key == idempotency_key,
                )
            )
        ).scalar_one_or_none()
        if existing is not None:
            return existing, False

        max_attempt = (
            await self.db.execute(
                select(func.coalesce(func.max(ActivityResult.attempt_no), 0)).where(
                    ActivityResult.user_id == user.id,
                    ActivityResult.activity_key == payload.activity_key,
                )
            )
        ).scalar_one()

        session = await self.touch_learning_session(user, payload.learning_session_id)
        record = ActivityResult(
            user_id=user.id,
            activity_key=payload.activity_key,
            module_key=payload.module_key,
            page_key=payload.page_key,
            learning_session_id=session.id if session else None,
            attempt_no=int(max_attempt) + 1,
            payload=payload.payload,
            idempotency_key=idempotency_key,
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record, True

    async def latest_activity_results(
        self, user: User, *, page_key: str | None = None
    ) -> list[ActivityResult]:
        stmt = select(ActivityResult).where(ActivityResult.user_id == user.id)
        if page_key:
            stmt = stmt.where(ActivityResult.page_key == page_key)
        stmt = stmt.order_by(ActivityResult.created_at.desc()).limit(100)
        rows = list((await self.db.execute(stmt)).scalars().all())
        seen: set[str] = set()
        latest: list[ActivityResult] = []
        for row in rows:
            if row.activity_key not in seen:
                seen.add(row.activity_key)
                latest.append(row)
        return latest

    # ── Events ──────────────────────────────────────────────────────────────

    async def ingest_events(
        self, user: User, events: list[EventIn], session_id: uuid.UUID | None
    ) -> tuple[int, uuid.UUID | None]:
        session = await self.touch_learning_session(user, session_id)
        resolved_session_id = session.id if session else None

        rows = [
            {
                "id": uuid.uuid4(),
                "user_id": user.id,
                "learning_session_id": resolved_session_id,
                "event_type": event.event_type.value,
                "module_key": event.module_key,
                "page_key": event.page_key,
                "activity_key": event.activity_key,
                "question_key": event.question_key,
                "section_id": event.section_id,
                # ORM attribute name; the column itself is "metadata".
                "event_metadata": event.metadata,
                "client_ts": event.client_ts,
            }
            for event in events
        ]
        if rows:
            # Single multi-row insert per batch.
            await self.db.execute(pg_insert(Event).values(rows))

        if resolved_session_id and any(
            e.event_type.value == "session_ended" for e in events
        ):
            await self.end_learning_session(user, resolved_session_id)

        await self.db.commit()
        return len(rows), resolved_session_id
