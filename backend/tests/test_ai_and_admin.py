"""AI service, role guards, health checks, and content-registry invariants."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AiMessage, User, UserRole
from app.services.content_registry import content_registry
from app.services.llm import LLMService
from app.services.llm.prompts import PROMPTS


# ── AI ───────────────────────────────────────────────────────────────────────


async def test_ai_chat_requires_authentication(client: AsyncClient):
    assert (await client.post("/api/v1/ai/chat", json={"message": "hello"})).status_code == 401


async def test_ai_chat_persists_messages(client: AsyncClient, learner, db: AsyncSession):
    response = await client.post(
        "/api/v1/ai/chat",
        headers=learner["headers"],
        json={"message": "What is overfitting?", "module_key": "module-4", "page_key": "m4p1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["content"]
    assert body["conversation_id"]
    assert body["usage"]["model"]

    messages = (await db.execute(select(AiMessage).order_by(AiMessage.created_at))).scalars().all()
    assert [message.role for message in messages] == ["user", "assistant"]
    assert all(str(message.user_id) == learner["user_id"] for message in messages)


async def test_ai_activity_returns_structured_verdict(client: AsyncClient, learner):
    response = await client.post(
        "/api/v1/ai/activity",
        headers=learner["headers"],
        json={"prompt_key": "fact_or_fiction", "input": "AI can diagnose any disease from a photo."},
    )
    assert response.status_code == 200
    structured = response.json()["structured"]
    assert structured is not None
    # Only allow-listed keys reach the client.
    assert set(structured).issubset(set(PROMPTS["fact_or_fiction"].json_keys))
    assert structured["verdict"]


async def test_ai_activity_rejects_unknown_prompt(client: AsyncClient, learner):
    response = await client.post(
        "/api/v1/ai/activity",
        headers=learner["headers"],
        json={"prompt_key": "not_a_prompt", "input": "hello there friend"},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "unknown_prompt"


async def test_ai_input_length_is_bounded(client: AsyncClient, learner):
    response = await client.post(
        "/api/v1/ai/chat", headers=learner["headers"], json={"message": "x" * 5000}
    )
    assert response.status_code == 422


async def test_ai_activity_context_is_bounded(client: AsyncClient, learner):
    response = await client.post(
        "/api/v1/ai/chat",
        headers=learner["headers"],
        json={"message": "help", "activity_context": {"blob": "y" * 3000}},
    )
    assert response.status_code == 422


async def test_ai_rate_limit(client: AsyncClient, learner, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "AI_RATE_LIMIT_PER_HOUR", 2)
    statuses = []
    for _ in range(4):
        response = await client.post(
            "/api/v1/ai/chat", headers=learner["headers"], json={"message": "hello"}
        )
        statuses.append(response.status_code)
    assert 429 in statuses, statuses


def test_tutor_context_never_contains_learner_records():
    """The tutor gets page structure, not learner data."""
    block = content_registry.tutor_context(
        module_key="module-4",
        page_key="m4p1",
        section_id="m4p1-boundary",
        activity_key="decision-boundary",
        activity_context={"k": 1, "train_accuracy": 0.99},
    )
    assert "Module: Machine Learning" in block
    assert "How Models Learn" in block
    assert "decision-boundary" in block
    assert "k=1" in block
    # No PII fields can appear because none are ever passed in.
    for forbidden in ("email", "@", "password", "user_id"):
        assert forbidden not in block.lower()


async def test_llm_service_reports_offline_mode(db: AsyncSession):
    service = LLMService(db)
    assert service.offline is True  # LLM_PROVIDER=echo in tests


# ── Roles ────────────────────────────────────────────────────────────────────


async def test_admin_routes_are_forbidden_for_learners(client: AsyncClient, learner):
    for path in (
        "/api/v1/admin/users",
        "/api/v1/admin/analytics/summary",
        "/api/v1/admin/export/events.csv",
        "/api/v1/admin/questions",
    ):
        response = await client.get(path, headers=learner["headers"])
        assert response.status_code == 403, path


async def test_instructor_can_read_admin_routes(client: AsyncClient, learner, db: AsyncSession):
    user = await db.get(User, learner["user_id"])
    assert user is not None
    user.role = UserRole.INSTRUCTOR.value
    await db.commit()

    summary = await client.get("/api/v1/admin/analytics/summary", headers=learner["headers"])
    assert summary.status_code == 200
    assert "users" in summary.json()

    export = await client.get("/api/v1/admin/export/responses.csv", headers=learner["headers"])
    assert export.status_code == 200
    assert export.headers["content-type"].startswith("text/csv")
    # The export is pseudonymized: user_id only, never email.
    header_row = export.text.splitlines()[0]
    assert "user_id" in header_row
    assert "email" not in header_row


async def test_role_claim_in_token_cannot_be_forged(client: AsyncClient, learner, db):
    """Authorization checks the loaded user row, not just the token claim."""
    import jwt

    from app.core.config import settings
    from app.core.security import decode_access_token

    payload = decode_access_token(learner["token"])
    forged = jwt.encode(
        {**payload, "role": "admin"}, settings.SECRET_KEY, algorithm="HS256"
    )
    response = await client.get(
        "/api/v1/admin/users", headers={"Authorization": f"Bearer {forged}"}
    )
    assert response.status_code == 403


# ── Health & content ─────────────────────────────────────────────────────────


async def test_health_returns_ok(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    versioned = await client.get("/api/v1/health")
    assert versioned.status_code == 200


async def test_readiness_checks_dependencies(client: AsyncClient):
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    names = {check["name"]: check["ok"] for check in body["checks"]}
    assert names["database"] is True
    assert names["content"] is True
    assert names["content_manifest"] is True


def test_content_manifest_is_valid():
    assert content_registry.validate() == []
    assert len(content_registry.modules) == 7
    for module in content_registry.modules:
        assert len(module["pages"]) == 2


def test_every_activity_has_tutor_guidance():
    guidance = content_registry.manifest.get("activityGuidance", {})
    for module in content_registry.modules:
        for page in module["pages"]:
            for section in page.get("sections", []):
                if section.get("kind") == "activity":
                    assert section["activity"] in guidance, section["activity"]


def test_every_ai_activity_has_a_backend_prompt():
    for module in content_registry.modules:
        for page in module["pages"]:
            for section in page.get("sections", []):
                if section.get("kind") == "aiActivity":
                    assert section["promptKey"] in PROMPTS, section["promptKey"]


async def test_unknown_route_returns_json_not_html(client: AsyncClient):
    response = await client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


async def test_oversized_body_is_rejected(client: AsyncClient, learner):
    response = await client.post(
        "/api/v1/events",
        headers={**learner["headers"], "Content-Length": "2000000"},
        content=b"{}",
    )
    assert response.status_code == 413
