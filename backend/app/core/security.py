"""Password hashing, JWT access tokens, opaque refresh tokens, and one-way hashing helpers."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from argon2.low_level import Type

from app.core.config import settings
from app.core.errors import Unauthorized

# Argon2id — OWASP-recommended parameters (64 MiB, 3 iterations, 4 lanes).
_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)

JWT_ALGORITHM = "HS256"
_DUMMY_HASH = _hasher.hash("aipassport-timing-equalizer")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    """Constant-ish time verification.

    When ``password_hash`` is None (no local identity) a dummy verification still runs so a
    non-existent account does not respond measurably faster than an existing one.
    """
    target = password_hash or _DUMMY_HASH
    try:
        _hasher.verify(target, password)
    except (VerifyMismatchError, InvalidHashError, Exception):  # noqa: BLE001 - never leak details
        return False
    return password_hash is not None


def needs_rehash(password_hash: str) -> bool:
    try:
        return _hasher.check_needs_rehash(password_hash)
    except Exception:  # noqa: BLE001
        return False


# ── Access tokens ────────────────────────────────────────────────────────────


def create_access_token(
    *,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    role: str,
    expires_minutes: int | None = None,
) -> tuple[str, datetime]:
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "sid": str(session_id),
        "role": role,
        "typ": "access",
        "jti": secrets.token_urlsafe(12),
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token, expires_at


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["exp", "sub", "sid"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise Unauthorized("Your session has expired.", code="token_expired") from exc
    except jwt.InvalidTokenError as exc:
        raise Unauthorized("Invalid authentication token.", code="invalid_token") from exc
    if payload.get("typ") != "access":
        raise Unauthorized("Invalid authentication token.", code="invalid_token")
    return payload


# ── Opaque tokens (refresh, password reset, email verification) ──────────────


def new_opaque_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    """Keyed one-way hash for tokens stored at rest."""
    return hmac.new(settings.SECRET_KEY.encode(), token.encode(), hashlib.sha256).hexdigest()


def constant_time_equals(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())


def hash_identifier(value: str) -> str:
    """Salted hash for low-sensitivity identifiers such as IP addresses."""
    return hashlib.sha256(f"{settings.HASH_SALT}:{value}".encode()).hexdigest()[:32]


def email_log_id(email: str) -> str:
    """Short non-reversible tag so auth failures are correlatable without logging the address."""
    return hashlib.sha256(f"{settings.HASH_SALT}:email:{email.lower()}".encode()).hexdigest()[:12]


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)
