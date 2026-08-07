"""Authentication and authorization dependencies.

``get_current_user`` is the single source of truth for identity. No route ever accepts a
client-supplied user id.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.errors import Forbidden, Unauthorized
from app.core.security import decode_access_token
from app.models import AuthSession, User, UserRole

_bearer = HTTPBearer(auto_error=False, description="Access token issued by /auth/login.")

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def _resolve_user(
    credentials: HTTPAuthorizationCredentials | None, db: AsyncSession
) -> User:
    if credentials is None or not credentials.credentials:
        raise Unauthorized()
    payload = decode_access_token(credentials.credentials)

    try:
        user_id = uuid.UUID(payload["sub"])
        session_id = uuid.UUID(payload["sid"])
    except (KeyError, ValueError) as exc:
        raise Unauthorized("Invalid authentication token.", code="invalid_token") from exc

    auth_session = await db.get(AuthSession, session_id)
    if (
        auth_session is None
        or auth_session.user_id != user_id
        or auth_session.revoked_at is not None
        or auth_session.expires_at <= datetime.now(UTC)
    ):
        raise Unauthorized("Your session is no longer valid.", code="session_revoked")

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise Unauthorized("Account is not available.", code="account_inactive")
    return user


async def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)] = None,
) -> User:
    return await _resolve_user(credentials, db)


async def get_optional_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)] = None,
) -> User | None:
    if credentials is None:
        return None
    try:
        return await _resolve_user(credentials, db)
    except Unauthorized:
        return None


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]

_ROLE_RANK = {UserRole.LEARNER: 0, UserRole.INSTRUCTOR: 1, UserRole.ADMIN: 2}


def require_role(minimum: UserRole) -> Callable[..., object]:
    """Role guard enforced against the loaded user row, not just the token claim."""

    async def _guard(user: CurrentUser) -> User:
        try:
            rank = _ROLE_RANK[UserRole(user.role)]
        except ValueError:
            rank = 0
        if rank < _ROLE_RANK[minimum]:
            raise Forbidden()
        return user

    return _guard


def request_user_agent(request: Request) -> str | None:
    ua = request.headers.get("user-agent")
    return ua[:400] if ua else None
