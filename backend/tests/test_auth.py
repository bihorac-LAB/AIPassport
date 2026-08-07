"""Authentication: registration, login, refresh rotation, logout, reset, rate limits."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rate_limit import limiter
from app.core.config import settings
from app.models import AuthSession, IdentityProvider, User, UserIdentity
from tests.conftest import unique_email


async def test_register_creates_user_and_local_identity(client: AsyncClient, db: AsyncSession):
    email = unique_email()
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correct-horse-9", "display_name": "Ada"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == email
    assert body["user"]["role"] == "learner"
    assert body["access_token"]
    assert settings.REFRESH_COOKIE_NAME in response.cookies

    user = (
        await db.execute(select(User).where(User.email == email))
    ).scalar_one()
    identity = (
        await db.execute(select(UserIdentity).where(UserIdentity.user_id == user.id))
    ).scalar_one()
    assert identity.provider == IdentityProvider.LOCAL.value
    # Password is hashed with Argon2id and the plaintext appears nowhere.
    assert identity.password_hash and identity.password_hash.startswith("$argon2id$")
    assert "correct-horse-9" not in identity.password_hash


async def test_register_rejects_duplicate_email(client: AsyncClient):
    email = unique_email()
    payload = {"email": email, "password": "correct-horse-9", "display_name": "Ada"}
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201
    duplicate = await client.post("/api/v1/auth/register", json=payload)
    assert duplicate.status_code == 409
    assert duplicate.json()["code"] == "email_registered"


async def test_register_rejects_weak_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": unique_email(), "password": "short", "display_name": "Ada"},
    )
    assert response.status_code == 422


async def test_login_and_me(client: AsyncClient, learner: dict[str, str]):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": learner["email"], "password": learner["password"]},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    me = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == learner["email"]


async def test_login_with_wrong_password_fails_identically(client: AsyncClient, learner):
    wrong = await client.post(
        "/api/v1/auth/login", json={"email": learner["email"], "password": "not-the-password"}
    )
    unknown = await client.post(
        "/api/v1/auth/login", json={"email": unique_email(), "password": "not-the-password"}
    )
    assert wrong.status_code == unknown.status_code == 401
    # Identical body: a caller cannot tell whether the account exists.
    assert wrong.json() == unknown.json()


async def test_protected_route_requires_token(client: AsyncClient):
    assert (await client.get("/api/v1/users/me")).status_code == 401
    bad = await client.get("/api/v1/users/me", headers={"Authorization": "Bearer nonsense"})
    assert bad.status_code == 401
    assert bad.json()["code"] == "invalid_token"


async def test_refresh_rotates_and_requires_csrf(client: AsyncClient, learner):
    login = await client.post(
        "/api/v1/auth/login", json={"email": learner["email"], "password": learner["password"]}
    )
    csrf = login.json()["csrf_token"]

    # Without the CSRF header the cookie alone is not enough.
    no_csrf = await client.post("/api/v1/auth/refresh")
    assert no_csrf.status_code == 403

    refreshed = await client.post("/api/v1/auth/refresh", headers={"X-CSRF-Token": csrf})
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"] != login.json()["access_token"]


async def test_refresh_reuse_revokes_session_family(client: AsyncClient, learner, db: AsyncSession):
    login = await client.post(
        "/api/v1/auth/login", json={"email": learner["email"], "password": learner["password"]}
    )
    stolen_cookie = login.cookies[settings.REFRESH_COOKIE_NAME]
    csrf = login.json()["csrf_token"]

    first = await client.post("/api/v1/auth/refresh", headers={"X-CSRF-Token": csrf})
    assert first.status_code == 200

    # Replaying the original (now rotated) token must revoke the whole family.
    replay = await client.post(
        "/api/v1/auth/refresh",
        headers={"X-CSRF-Token": csrf},
        cookies={settings.REFRESH_COOKIE_NAME: stolen_cookie, settings.CSRF_COOKIE_NAME: csrf},
    )
    assert replay.status_code == 401
    assert replay.json()["code"] == "refresh_reuse"

    # Only the compromised family is revoked — a different device's session stays valid, which is
    # why the assertion is scoped to the family the leaked token belonged to.
    user_id = login.json()["user"]["id"]
    sessions = (
        (await db.execute(select(AuthSession).where(AuthSession.user_id == user_id)))
        .scalars()
        .all()
    )
    compromised_family = next(
        session.family_id for session in sessions if session.rotated_to_id is not None
    )
    family = [session for session in sessions if session.family_id == compromised_family]
    assert len(family) >= 2
    assert all(session.revoked_at is not None for session in family)


async def test_logout_revokes_and_access_token_stops_working(client: AsyncClient, learner):
    login = await client.post(
        "/api/v1/auth/login", json={"email": learner["email"], "password": learner["password"]}
    )
    token = login.json()["access_token"]
    csrf = login.json()["csrf_token"]

    assert (
        await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    ).status_code == 200

    logout = await client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf})
    assert logout.status_code == 200

    # The access token is still cryptographically valid but its session is revoked.
    after = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert after.status_code == 401
    assert after.json()["code"] == "session_revoked"


async def test_password_reset_does_not_reveal_account_existence(client: AsyncClient, learner):
    known = await client.post(
        "/api/v1/auth/password-reset/request", json={"email": learner["email"]}
    )
    unknown = await client.post(
        "/api/v1/auth/password-reset/request", json={"email": unique_email()}
    )
    assert known.status_code == unknown.status_code == 200
    assert known.json() == unknown.json()


async def test_password_reset_end_to_end(client: AsyncClient, learner, db: AsyncSession):
    from app.services.auth_service import AuthService

    service = AuthService(db)
    token = await service.create_password_reset(learner["email"])
    assert token

    confirm = await client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": token, "new_password": "brand-new-passphrase-7"},
    )
    assert confirm.status_code == 200

    # Old password no longer works; new one does.
    assert (
        await client.post(
            "/api/v1/auth/login",
            json={"email": learner["email"], "password": learner["password"]},
        )
    ).status_code == 401
    assert (
        await client.post(
            "/api/v1/auth/login",
            json={"email": learner["email"], "password": "brand-new-passphrase-7"},
        )
    ).status_code == 200

    # Single use.
    reuse = await client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": token, "new_password": "another-passphrase-8"},
    )
    assert reuse.status_code == 400


async def test_login_rate_limit(client: AsyncClient, learner):
    limiter.reset()
    statuses = []
    for _ in range(7):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": learner["email"], "password": "wrong-password-here"},
        )
        statuses.append(response.status_code)
    assert 429 in statuses, statuses
    limited = [s for s in statuses if s == 429]
    assert len(limited) >= 1


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "not-an-email", "password": "correct-horse-9", "display_name": "A"},
        {"email": "a@b.co", "password": "correct-horse-9"},
        {"email": "a@b.co", "password": "correct-horse-9", "display_name": "A", "role": "admin"},
    ],
)
async def test_register_validation(client: AsyncClient, payload: dict[str, str]):
    """The third case matters most: a client cannot grant itself a role."""
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 422
