"""Curriculum, progress, response, event, and AI schemas.

Note what is *absent* from every write schema: ``user_id``. The authenticated user is resolved
server-side from the access token, and ``extra='forbid'`` means a client that tries to supply one is
rejected rather than silently trusted.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import Field, field_validator

from app.models.enums import EventType, PageKind, ProgressStatus, QuestionType
from app.schemas.common import Json, ORMModel, StrictModel

KeyStr = Annotated[str, Field(min_length=1, max_length=96, pattern=r"^[A-Za-z0-9._-]+$")]


# ── Curriculum ───────────────────────────────────────────────────────────────


class QuestionOut(ORMModel):
    key: str
    position: int
    type: QuestionType
    prompt: str
    spec: Json
    version: int
    is_graded: bool


class PageProgressOut(ORMModel):
    page_key: str
    module_key: str
    status: ProgressStatus
    sections_completed: list[str]
    last_section_id: str | None
    seconds_spent: int
    visit_count: int
    completed_at: datetime | None
    updated_at: datetime


class ModulePageOut(ORMModel):
    key: str
    module_key: str
    position: int
    slug: str
    title: str
    kicker: str
    kind: PageKind
    objectives: list[str]
    required_sections: list[str]
    estimated_minutes: int
    content_version: int


class ModulePageDetail(ModulePageOut):
    questions: list[QuestionOut] = []
    progress: PageProgressOut | None = None


class ModuleOut(ORMModel):
    key: str
    position: int
    title: str
    subtitle: str
    summary: str
    accent: str
    content_version: int
    pages: list[ModulePageOut] = []


class ModuleSummary(ModuleOut):
    pages_completed: int = 0
    pages_total: int = 0
    status: ProgressStatus = ProgressStatus.NOT_STARTED


class ModuleDetail(ModuleOut):
    pages: list[ModulePageDetail] = []


# ── Learning sessions ────────────────────────────────────────────────────────


class LearningSessionStart(StrictModel):
    is_embedded: bool = False
    timezone: str | None = Field(default=None, max_length=64)
    viewport_width: int | None = Field(default=None, ge=0, le=20000)
    referrer_kind: Literal["direct", "canvas", "other"] | None = None


class LearningSessionOut(ORMModel):
    id: uuid.UUID
    started_at: datetime
    last_seen_at: datetime
    ended_at: datetime | None
    is_embedded: bool


# ── Progress ─────────────────────────────────────────────────────────────────


class ProgressUpdate(StrictModel):
    status: Literal["in_progress", "completed"] | None = None
    section_completed: KeyStr | None = None
    last_section_id: KeyStr | None = None
    # Bounded so a client cannot inflate time-on-task with one huge number.
    seconds_delta: int = Field(default=0, ge=0, le=600)
    register_visit: bool = False
    learning_session_id: uuid.UUID | None = None


class ResumePointer(ORMModel):
    module_key: str
    page_key: str
    section_id: str | None = None


class ProgressOverview(ORMModel):
    pages: list[PageProgressOut]
    modules_completed: list[str]
    total_seconds: int
    resume: ResumePointer | None = None


# ── Question responses ───────────────────────────────────────────────────────


class ResponseCreate(StrictModel):
    question_key: KeyStr
    # Free-form but bounded; the shape is validated per question type by the service.
    answer: Json
    is_final: bool = True
    response_time_ms: int | None = Field(default=None, ge=0, le=86_400_000)
    client_submitted_at: datetime | None = None
    learning_session_id: uuid.UUID | None = None
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=128)

    @field_validator("answer")
    @classmethod
    def _bound_answer(cls, value: Json) -> Json:
        if len(value) > 40:
            raise ValueError("Answer payload has too many fields.")
        return value


class ResponseOut(ORMModel):
    id: uuid.UUID
    question_key: str
    question_version: int
    module_key: str
    page_key: str
    attempt_no: int
    answer: Json
    is_final: bool
    is_correct: bool | None
    score: float | None
    created_at: datetime


class ResponseResult(ORMModel):
    response: ResponseOut
    feedback: str | None = None
    explanation: str | None = None
    correct_answer: Any | None = None


class ActivityResultCreate(StrictModel):
    activity_key: KeyStr
    module_key: KeyStr
    page_key: KeyStr
    payload: Json
    learning_session_id: uuid.UUID | None = None
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=128)


class ActivityResultOut(ORMModel):
    id: uuid.UUID
    activity_key: str
    module_key: str
    page_key: str
    attempt_no: int
    payload: Json
    created_at: datetime


# ── Events ───────────────────────────────────────────────────────────────────


class EventIn(StrictModel):
    event_type: EventType
    module_key: KeyStr | None = None
    page_key: KeyStr | None = None
    activity_key: KeyStr | None = None
    question_key: KeyStr | None = None
    section_id: KeyStr | None = None
    metadata: Json = Field(default_factory=dict)
    client_ts: datetime | None = None

    @field_validator("metadata")
    @classmethod
    def _bound_metadata(cls, value: Json) -> Json:
        if len(value) > 20:
            raise ValueError("Event metadata has too many keys (max 20).")
        for key, item in value.items():
            if isinstance(item, str) and len(item) > 500:
                raise ValueError(f"Event metadata field '{key}' is too long (max 500 characters).")
        return value


class EventBatch(StrictModel):
    events: list[EventIn] = Field(min_length=1, max_length=50)
    learning_session_id: uuid.UUID | None = None


class EventBatchResult(ORMModel):
    accepted: int
    learning_session_id: uuid.UUID | None = None


# ── AI ───────────────────────────────────────────────────────────────────────


class AiChatMessage(StrictModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class AiChatRequest(StrictModel):
    message: str = Field(min_length=1, max_length=4000)
    module_key: KeyStr | None = None
    page_key: KeyStr | None = None
    section_id: KeyStr | None = None
    activity_key: KeyStr | None = None
    # Bounded, allow-listed summary of what the learner is looking at. Never learner records.
    activity_context: Json | None = None
    history: list[AiChatMessage] = Field(default_factory=list, max_length=10)
    conversation_id: uuid.UUID | None = None

    @field_validator("activity_context")
    @classmethod
    def _bound_context(cls, value: Json | None) -> Json | None:
        if value is None:
            return None
        if len(value) > 20:
            raise ValueError("activity_context has too many keys (max 20).")
        rendered = str(value)
        if len(rendered) > 2000:
            raise ValueError("activity_context is too large (max 2000 characters).")
        return value


class AiUsage(ORMModel):
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    latency_ms: int | None = None


class AiChatResponse(ORMModel):
    content: str
    conversation_id: uuid.UUID
    usage: AiUsage


class AiActivityRequest(StrictModel):
    prompt_key: KeyStr
    input: str = Field(min_length=1, max_length=6000)
    module_key: KeyStr | None = None
    page_key: KeyStr | None = None


class AiActivityResponse(ORMModel):
    prompt_key: str
    content: str | None = None
    structured: Json | None = None
    conversation_id: uuid.UUID
    usage: AiUsage
