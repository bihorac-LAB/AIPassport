"""Enumerations shared by the ORM and the API schemas."""

from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    LEARNER = "learner"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class IdentityProvider(StrEnum):
    LOCAL = "local"
    CANVAS_LTI = "canvas_lti"
    UF_SSO = "uf_sso"


class Track(StrEnum):
    CLINICAL = "clinical"
    BASIC = "basic"


class PageKind(StrEnum):
    EXPLORE = "explore"
    APPLY = "apply"


class ProgressStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class QuestionType(StrEnum):
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"
    FREE_TEXT = "free_text"
    NUMERIC = "numeric"
    LIKERT = "likert"
    SLIDER_ESTIMATE = "slider_estimate"
    STRUCTURED = "structured"


class EventType(StrEnum):
    """Server-enforced allowlist. Anything not listed here is rejected."""

    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    MODULE_OPENED = "module_opened"
    MODULE_COMPLETED = "module_completed"
    PAGE_VIEWED = "page_viewed"
    PAGE_COMPLETED = "page_completed"
    PAGE_SECTION_COMPLETED = "page_section_completed"
    ACTIVITY_STARTED = "activity_started"
    ACTIVITY_COMPLETED = "activity_completed"
    ACTIVITY_RESET = "activity_reset"
    QUESTION_VIEWED = "question_viewed"
    QUESTION_ANSWERED = "question_answered"
    PREDICTION_SUBMITTED = "prediction_submitted"
    SIMULATION_RUN = "simulation_run"
    PARAMETER_CHANGED = "parameter_changed"
    HINT_OPENED = "hint_opened"
    EXPLANATION_OPENED = "explanation_opened"
    AI_TUTOR_OPENED = "ai_tutor_opened"
    AI_MESSAGE_SENT = "ai_message_sent"
    NAVIGATION = "navigation"


class AiMessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
