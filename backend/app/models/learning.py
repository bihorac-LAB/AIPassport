"""Learner data.

Every table here references ``user_id`` (an internal UUID) and nothing else — no email, no display
name, no institutional identifier. ``question_responses``, ``activity_results`` and ``events`` are
append-only; ``page_progress`` is the only mutable projection.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, uuid_pk
from app.models.enums import ProgressStatus


class LearningSession(Base):
    """A study sitting. Distinct from an auth session: one login can span several sittings."""

    __tablename__ = "learning_sessions"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_embedded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    client_meta: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    __table_args__ = (
        Index("ix_learning_sessions_user_started", "user_id", "started_at"),
    )


class PageProgress(Base, TimestampMixin):
    __tablename__ = "page_progress"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    page_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("module_pages.id", ondelete="CASCADE"), nullable=False
    )
    module_key: Mapped[str] = mapped_column(String(64), nullable=False)
    page_key: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ProgressStatus.IN_PROGRESS.value
    )
    sections_completed: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    last_section_id: Mapped[str | None] = mapped_column(String(96), nullable=True)
    seconds_spent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    visit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "page_id", name="uq_page_progress_user_id_page_id"),
        Index("ix_page_progress_user_status", "user_id", "status"),
    )


class QuestionResponse(Base):
    """Append-only attempt log.

    A resubmission creates a new row with ``attempt_no + 1``; the previous attempt is retained and
    only its ``is_final`` flag is cleared. Nothing a learner submits is ever overwritten.
    """

    __tablename__ = "question_responses"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    question_key: Mapped[str] = mapped_column(String(96), nullable=False)
    question_version: Mapped[int] = mapped_column(Integer, nullable=False)
    module_key: Mapped[str] = mapped_column(String(64), nullable=False)
    page_key: Mapped[str] = mapped_column(String(64), nullable=False)
    learning_session_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("learning_sessions.id", ondelete="SET NULL"), nullable=True
    )
    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    answer: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    is_final: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    client_submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Scoped per user, not globally: two learners submitting the same answer to the same question
    # produce the same natural key, and one must not block the other.
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    # Server timestamp is the authoritative one.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "question_id", "attempt_no", name="uq_question_responses_user_question_attempt"
        ),
        UniqueConstraint(
            "user_id", "idempotency_key", name="uq_question_responses_user_idempotency"
        ),
        Index("ix_question_responses_user_question", "user_id", "question_key", "attempt_no"),
        Index(
            "ix_question_responses_final",
            "question_key",
            postgresql_where=text("is_final"),
        ),
        Index("ix_question_responses_page", "user_id", "page_key"),
    )


class ActivityResult(Base):
    """Structured output of a simulator or multi-step activity. Append-only."""

    __tablename__ = "activity_results"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    activity_key: Mapped[str] = mapped_column(String(96), nullable=False)
    module_key: Mapped[str] = mapped_column(String(64), nullable=False)
    page_key: Mapped[str] = mapped_column(String(64), nullable=False)
    learning_session_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("learning_sessions.id", ondelete="SET NULL"), nullable=True
    )
    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    # Scoped per user for the same reason as question_responses.
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        UniqueConstraint("user_id", "idempotency_key", name="uq_activity_results_user_idempotency"),
        Index("ix_activity_results_user_activity", "user_id", "activity_key"),
    )


class Event(Base):
    """Analytics stream. Append-only; ``created_at`` is authoritative."""

    __tablename__ = "events"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    learning_session_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("learning_sessions.id", ondelete="SET NULL"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(48), nullable=False)
    module_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    page_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    activity_key: Mapped[str | None] = mapped_column(String(96), nullable=True)
    question_key: Mapped[str | None] = mapped_column(String(96), nullable=True)
    section_id: Mapped[str | None] = mapped_column(String(96), nullable=True)
    event_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    client_ts: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        Index("ix_events_user_created", "user_id", "created_at"),
        Index("ix_events_type_created", "event_type", "created_at"),
        Index("ix_events_module_page", "module_key", "page_key"),
        Index("ix_events_session", "learning_session_id"),
    )


class AiConversation(Base, TimestampMixin):
    __tablename__ = "ai_conversations"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False, default="tutor")
    module_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    page_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prompt_key: Mapped[str | None] = mapped_column(String(64), nullable=True)

    __table_args__ = (Index("ix_ai_conversations_user", "user_id", "created_at"),)


class AiMessage(Base):
    __tablename__ = "ai_messages"

    id: Mapped[uuid.UUID] = uuid_pk()
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str | None] = mapped_column(String(96), nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(48), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (Index("ix_ai_messages_conversation", "conversation_id", "created_at"),)
