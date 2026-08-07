"""Curriculum, responses, events, progress, and attribution."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, ModulePage, QuestionResponse
from tests.conftest import unique_email


# ── Curriculum ───────────────────────────────────────────────────────────────


async def test_every_module_has_exactly_two_pages(client: AsyncClient, db: AsyncSession):
    response = await client.get("/api/v1/modules")
    assert response.status_code == 200
    modules = response.json()
    assert len(modules) == 7
    for module in modules:
        assert len(module["pages"]) == 2, f"{module['key']} has {len(module['pages'])} pages"
        assert [page["position"] for page in module["pages"]] == [1, 2]

    # And the invariant holds in the database, not just in the response.
    counts = (
        await db.execute(
            select(ModulePage.module_key, func.count()).group_by(ModulePage.module_key)
        )
    ).all()
    assert all(count == 2 for _, count in counts)
    assert len(counts) == 7


async def test_page_detail_includes_questions(client: AsyncClient):
    response = await client.get("/api/v1/modules/module-1/pages/m1p1")
    assert response.status_code == 200
    body = response.json()
    assert body["key"] == "m1p1"
    assert body["kind"] == "explore"
    assert len(body["questions"]) >= 1
    question = body["questions"][0]
    assert question["key"].startswith("m1p1.")
    # The correct answer is not exposed before submission would be ideal, but the spec is needed
    # client-side for rendering options; correctness is still decided server-side.
    assert "options" in question["spec"]


async def test_page_from_wrong_module_is_404(client: AsyncClient):
    assert (await client.get("/api/v1/modules/module-2/pages/m1p1")).status_code == 404


async def test_unknown_module_is_404(client: AsyncClient):
    assert (await client.get("/api/v1/modules/module-99")).status_code == 404


# ── Responses ────────────────────────────────────────────────────────────────


async def test_response_requires_authentication(client: AsyncClient):
    response = await client.post(
        "/api/v1/responses", json={"question_key": "m1p1.q1", "answer": {"value": "no_rules"}}
    )
    assert response.status_code == 401


async def test_client_supplied_user_id_is_rejected(client: AsyncClient, learner):
    """The core attribution guarantee: the backend never trusts a client user id."""
    response = await client.post(
        "/api/v1/responses",
        headers=learner["headers"],
        json={
            "question_key": "m1p1.q1",
            "answer": {"value": "no_rules"},
            "user_id": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


async def test_response_is_attributed_to_the_authenticated_user(
    client: AsyncClient, learner, db: AsyncSession
):
    response = await client.post(
        "/api/v1/responses",
        headers=learner["headers"],
        json={"question_key": "m1p1.q1", "answer": {"value": "no_rules"}},
    )
    assert response.status_code == 201
    record = (await db.execute(select(QuestionResponse))).scalars().one()
    assert str(record.user_id) == learner["user_id"]
    assert record.question_key == "m1p1.q1"
    assert record.module_key == "module-1"
    assert record.page_key == "m1p1"
    assert record.created_at is not None  # server timestamp is authoritative


async def test_grading_happens_server_side(client: AsyncClient, learner):
    correct = await client.post(
        "/api/v1/responses",
        headers=learner["headers"],
        json={"question_key": "m1p1.q1", "answer": {"value": "no_rules"}},
    )
    assert correct.json()["response"]["is_correct"] is True
    assert correct.json()["explanation"]

    wrong = await client.post(
        "/api/v1/responses",
        headers=learner["headers"],
        json={"question_key": "m1p1.q1", "answer": {"value": "yes_data"}},
    )
    assert wrong.json()["response"]["is_correct"] is False


async def test_attempts_are_append_only(client: AsyncClient, learner, db: AsyncSession):
    for value in ("no_rules", "yes_data", "yes_ai"):
        response = await client.post(
            "/api/v1/responses",
            headers=learner["headers"],
            json={"question_key": "m1p1.q1", "answer": {"value": value}},
        )
        assert response.status_code == 201

    records = (
        (
            await db.execute(
                select(QuestionResponse)
                .where(QuestionResponse.question_key == "m1p1.q1")
                .order_by(QuestionResponse.attempt_no)
            )
        )
        .scalars()
        .all()
    )
    assert [record.attempt_no for record in records] == [1, 2, 3]
    # Exactly one is final; earlier attempts are retained, not overwritten.
    assert [record.is_final for record in records] == [False, False, True]

    history = await client.get(
        "/api/v1/responses/me/m1p1.q1/history", headers=learner["headers"]
    )
    assert len(history.json()) == 3


async def test_idempotency_key_prevents_duplicate_attempts(client: AsyncClient, learner, db):
    payload = {
        "question_key": "m1p1.q1",
        "answer": {"value": "no_rules"},
        "idempotency_key": "fixed-key-for-this-test",
    }
    first = await client.post("/api/v1/responses", headers=learner["headers"], json=payload)
    second = await client.post("/api/v1/responses", headers=learner["headers"], json=payload)
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["response"]["id"] == second.json()["response"]["id"]

    count = (await db.execute(select(func.count()).select_from(QuestionResponse))).scalar_one()
    assert count == 1


async def test_two_learners_can_submit_the_same_answer(client: AsyncClient, learner, db):
    """Idempotency is scoped per user.

    The client derives its key from question + answer, so two learners answering identically produce
    the same key. Global uniqueness would have let one learner block the other.
    """
    payload = {
        "question_key": "m1p1.q1",
        "answer": {"value": "no_rules"},
        "idempotency_key": "shared-natural-key",
    }
    first = await client.post("/api/v1/responses", headers=learner["headers"], json=payload)
    assert first.status_code == 201

    other = await client.post(
        "/api/v1/auth/register",
        json={"email": unique_email("other"), "password": "correct-horse-9", "display_name": "B"},
    )
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}
    second = await client.post("/api/v1/responses", headers=other_headers, json=payload)
    assert second.status_code == 201
    assert second.json()["response"]["id"] != first.json()["response"]["id"]

    count = (await db.execute(select(func.count()).select_from(QuestionResponse))).scalar_one()
    assert count == 2


async def test_idempotency_key_conflict_on_different_answer(client: AsyncClient, learner):
    key = "conflicting-key-1"
    await client.post(
        "/api/v1/responses",
        headers=learner["headers"],
        json={"question_key": "m1p1.q1", "answer": {"value": "no_rules"}, "idempotency_key": key},
    )
    conflict = await client.post(
        "/api/v1/responses",
        headers=learner["headers"],
        json={"question_key": "m1p1.q1", "answer": {"value": "yes_data"}, "idempotency_key": key},
    )
    assert conflict.status_code == 409


async def test_invalid_answer_shape_is_rejected(client: AsyncClient, learner):
    bad_option = await client.post(
        "/api/v1/responses",
        headers=learner["headers"],
        json={"question_key": "m1p1.q1", "answer": {"value": "not-an-option"}},
    )
    assert bad_option.status_code == 400
    assert bad_option.json()["code"] == "answer_invalid"

    wrong_shape = await client.post(
        "/api/v1/responses",
        headers=learner["headers"],
        json={"question_key": "m1p1.q1", "answer": {"values": ["no_rules"]}},
    )
    assert wrong_shape.status_code == 400


async def test_free_text_min_length_enforced(client: AsyncClient, learner):
    short = await client.post(
        "/api/v1/responses",
        headers=learner["headers"],
        json={"question_key": "m1p2.q3", "answer": {"text": "too short"}},
    )
    assert short.status_code == 400
    assert short.json()["code"] == "answer_too_short"

    long_enough = "In our registry, creatinine above 8 is usually real because those patients are on dialysis, whereas values under 0.2 are unit errors."
    ok = await client.post(
        "/api/v1/responses",
        headers=learner["headers"],
        json={"question_key": "m1p2.q3", "answer": {"text": long_enough}},
    )
    assert ok.status_code == 201
    assert ok.json()["response"]["is_correct"] is None  # ungraded reflection


async def test_slider_estimate_range_grading(client: AsyncClient, learner):
    inside = await client.post(
        "/api/v1/responses",
        headers=learner["headers"],
        json={"question_key": "m4p2.q2", "answer": {"value": 8}},
    )
    assert inside.json()["response"]["is_correct"] is True

    outside = await client.post(
        "/api/v1/responses",
        headers=learner["headers"],
        json={"question_key": "m4p2.q2", "answer": {"value": 90}},
    )
    assert outside.json()["response"]["is_correct"] is False


async def test_multi_choice_partial_credit(client: AsyncClient, learner):
    response = await client.post(
        "/api/v1/responses",
        headers=learner["headers"],
        json={"question_key": "m1p1.q2", "answer": {"values": ["data", "compute"]}},
    )
    body = response.json()["response"]
    assert body["is_correct"] is False  # missing one correct option
    assert 0 < (body["score"] or 0) < 1


async def test_responses_are_scoped_to_the_caller(client: AsyncClient, learner):
    await client.post(
        "/api/v1/responses",
        headers=learner["headers"],
        json={"question_key": "m1p1.q1", "answer": {"value": "no_rules"}},
    )

    other = await client.post(
        "/api/v1/auth/register",
        json={"email": unique_email("other"), "password": "correct-horse-9", "display_name": "B"},
    )
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    mine = await client.get("/api/v1/responses/me", headers=learner["headers"])
    theirs = await client.get("/api/v1/responses/me", headers=other_headers)
    assert len(mine.json()) == 1
    assert theirs.json() == []


# ── Events ───────────────────────────────────────────────────────────────────


async def test_event_batch_persists_with_server_timestamp(client: AsyncClient, learner, db):
    session = await client.post(
        "/api/v1/sessions", headers=learner["headers"], json={"is_embedded": False}
    )
    session_id = session.json()["id"]

    response = await client.post(
        "/api/v1/events",
        headers=learner["headers"],
        json={
            "learning_session_id": session_id,
            "events": [
                {"event_type": "page_viewed", "module_key": "module-1", "page_key": "m1p1"},
                {
                    "event_type": "parameter_changed",
                    "module_key": "module-1",
                    "activity_key": "outlier-lab",
                    "metadata": {"parameters": {"multiplier": 1.5}, "interaction_count": 7},
                },
            ],
        },
    )
    assert response.status_code == 202
    assert response.json()["accepted"] == 2

    events = (await db.execute(select(Event).order_by(Event.created_at))).scalars().all()
    assert len(events) == 2
    assert all(str(event.user_id) == learner["user_id"] for event in events)
    assert all(event.created_at is not None for event in events)
    assert str(events[0].learning_session_id) == session_id
    assert events[1].event_metadata["interaction_count"] == 7


async def test_unknown_event_type_is_rejected(client: AsyncClient, learner, db):
    response = await client.post(
        "/api/v1/events",
        headers=learner["headers"],
        json={"events": [{"event_type": "mouse_moved"}]},
    )
    assert response.status_code == 422
    count = (await db.execute(select(func.count()).select_from(Event))).scalar_one()
    assert count == 0


async def test_event_batch_size_and_metadata_limits(client: AsyncClient, learner):
    too_many = await client.post(
        "/api/v1/events",
        headers=learner["headers"],
        json={"events": [{"event_type": "navigation"} for _ in range(51)]},
    )
    assert too_many.status_code == 422

    huge_field = await client.post(
        "/api/v1/events",
        headers=learner["headers"],
        json={"events": [{"event_type": "navigation", "metadata": {"path": "x" * 600}}]},
    )
    assert huge_field.status_code == 422


async def test_events_require_authentication(client: AsyncClient):
    response = await client.post(
        "/api/v1/events", json={"events": [{"event_type": "navigation"}]}
    )
    assert response.status_code == 401


# ── Progress ─────────────────────────────────────────────────────────────────


async def test_progress_accumulates_and_completes(client: AsyncClient, learner):
    page = (await client.get("/api/v1/modules/module-1/pages/m1p1")).json()
    required = page["required_sections"]
    assert required

    for index, section in enumerate(required):
        response = await client.post(
            f"/api/v1/progress/pages/m1p1",
            headers=learner["headers"],
            json={
                "section_completed": section,
                "last_section_id": section,
                "seconds_delta": 20,
                "register_visit": index == 0,
            },
        )
        assert response.status_code == 200

    final = response.json()
    assert final["status"] == "completed"
    assert final["completed_at"] is not None
    assert set(final["sections_completed"]) == set(required)
    assert final["seconds_spent"] == 20 * len(required)
    assert final["visit_count"] == 1


async def test_progress_rejects_implausible_time_delta(client: AsyncClient, learner):
    response = await client.post(
        "/api/v1/progress/pages/m1p1",
        headers=learner["headers"],
        json={"seconds_delta": 999_999},
    )
    assert response.status_code == 422


async def test_progress_caps_time_delta_at_configured_maximum(client: AsyncClient, learner):
    response = await client.post(
        "/api/v1/progress/pages/m1p1", headers=learner["headers"], json={"seconds_delta": 600}
    )
    # The schema allows up to 600 but the service caps each increment at MAX_TIME_DELTA_SECONDS.
    assert response.json()["seconds_spent"] == 120


async def test_module_completion_is_derived_from_both_pages(client: AsyncClient, learner):
    for page_key in ("m1p1", "m1p2"):
        page = (await client.get(f"/api/v1/modules/module-1/pages/{page_key}")).json()
        for section in page["required_sections"]:
            await client.post(
                f"/api/v1/progress/pages/{page_key}",
                headers=learner["headers"],
                json={"section_completed": section},
            )

    overview = await client.get("/api/v1/progress/me", headers=learner["headers"])
    assert overview.status_code == 200
    assert "module-1" in overview.json()["modules_completed"]
    assert overview.json()["resume"]["module_key"] == "module-1"


async def test_progress_is_scoped_to_the_caller(client: AsyncClient, learner):
    await client.post(
        "/api/v1/progress/pages/m1p1",
        headers=learner["headers"],
        json={"section_completed": "m1p1-q1"},
    )
    other = await client.post(
        "/api/v1/auth/register",
        json={"email": unique_email("other"), "password": "correct-horse-9", "display_name": "B"},
    )
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}
    overview = await client.get("/api/v1/progress/me", headers=other_headers)
    assert overview.json()["pages"] == []


# ── Activity results ─────────────────────────────────────────────────────────


async def test_activity_result_persists(client: AsyncClient, learner):
    response = await client.post(
        "/api/v1/activity-results",
        headers=learner["headers"],
        json={
            "activity_key": "model-card-builder",
            "module_key": "module-2",
            "page_key": "m2p2",
            "payload": {"intendedUse": "ED triage", "outOfScope": "Not for paediatrics"},
        },
    )
    assert response.status_code == 201
    assert response.json()["attempt_no"] == 1

    mine = await client.get("/api/v1/activity-results/me?page_key=m2p2", headers=learner["headers"])
    assert len(mine.json()) == 1
    assert mine.json()[0]["payload"]["intendedUse"] == "ED triage"
