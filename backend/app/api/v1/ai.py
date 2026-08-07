"""AI tutor and AI-powered activities.

The provider credential exists only in this process's environment. The browser talks to FastAPI,
FastAPI talks to the model.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.auth.dependencies import CurrentUser, DbSession
from app.auth.rate_limit import limiter
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.learning import (
    AiActivityRequest,
    AiActivityResponse,
    AiChatRequest,
    AiChatResponse,
    AiUsage,
)
from app.services.llm import LLMService

router = APIRouter(prefix="/ai", tags=["ai"])
log = get_logger("aipassport.ai.api")


def _rate_limit(user_id: str) -> None:
    limiter.check("ai:hour", user_id, limit=settings.AI_RATE_LIMIT_PER_HOUR, window_seconds=3600)
    limiter.check("ai:day", user_id, limit=settings.AI_RATE_LIMIT_PER_DAY, window_seconds=86400)


@router.post("/chat", response_model=AiChatResponse)
async def chat(payload: AiChatRequest, db: DbSession, user: CurrentUser) -> AiChatResponse:
    _rate_limit(str(user.id))
    service = LLMService(db)
    content, conversation_id, completion = await service.tutor_chat(
        user,
        message=payload.message,
        module_key=payload.module_key,
        page_key=payload.page_key,
        section_id=payload.section_id,
        activity_key=payload.activity_key,
        activity_context=payload.activity_context,
        history=[(m.role, m.content) for m in payload.history],
        conversation_id=payload.conversation_id,
    )
    log.info(
        "ai_chat",
        user_id=str(user.id),
        module=payload.module_key,
        page=payload.page_key,
        latency_ms=completion.latency_ms,
    )
    return AiChatResponse(
        content=content,
        conversation_id=conversation_id,
        usage=AiUsage(
            model=completion.model,
            prompt_tokens=completion.prompt_tokens,
            completion_tokens=completion.completion_tokens,
            latency_ms=completion.latency_ms,
        ),
    )


@router.post("/activity", response_model=AiActivityResponse)
async def run_activity(
    payload: AiActivityRequest, db: DbSession, user: CurrentUser
) -> AiActivityResponse:
    _rate_limit(str(user.id))
    service = LLMService(db)
    content, structured, conversation_id, completion = await service.run_activity(
        user,
        prompt_key=payload.prompt_key,
        user_input=payload.input,
        module_key=payload.module_key,
        page_key=payload.page_key,
    )
    log.info(
        "ai_activity",
        user_id=str(user.id),
        prompt=payload.prompt_key,
        latency_ms=completion.latency_ms,
    )
    return AiActivityResponse(
        prompt_key=payload.prompt_key,
        content=content,
        structured=structured,
        conversation_id=conversation_id,
        usage=AiUsage(
            model=completion.model,
            prompt_tokens=completion.prompt_tokens,
            completion_tokens=completion.completion_tokens,
            latency_ms=completion.latency_ms,
        ),
    )
