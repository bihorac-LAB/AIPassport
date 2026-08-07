"""Refresh + CSRF cookie handling.

The refresh token is ``HttpOnly`` so JavaScript cannot read it. It is scoped to the auth path so it
is not attached to ordinary API calls. Because the SPA is cross-site (Netlify → EC2) and must also
work in a Canvas iframe, ``SameSite=None; Secure`` is used in production; that is paired with a
strict CORS allowlist and a double-submit CSRF token.
"""

from __future__ import annotations

from fastapi import Request, Response

from app.core.config import settings
from app.core.errors import Forbidden

REFRESH_PATH = f"{settings.API_V1_PREFIX}/auth"


def set_refresh_cookie(response: Response, token: str, max_age_seconds: int) -> None:
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=token,
        max_age=max_age_seconds,
        path=REFRESH_PATH,
        domain=settings.COOKIE_DOMAIN,
        secure=settings.COOKIE_SECURE,
        httponly=True,
        samesite=settings.COOKIE_SAMESITE,
    )


def set_csrf_cookie(response: Response, token: str, max_age_seconds: int) -> None:
    # Deliberately readable by JS: the client echoes it in the X-CSRF-Token header.
    response.set_cookie(
        key=settings.CSRF_COOKIE_NAME,
        value=token,
        max_age=max_age_seconds,
        path="/",
        domain=settings.COOKIE_DOMAIN,
        secure=settings.COOKIE_SECURE,
        httponly=False,
        samesite=settings.COOKIE_SAMESITE,
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        settings.REFRESH_COOKIE_NAME, path=REFRESH_PATH, domain=settings.COOKIE_DOMAIN
    )
    response.delete_cookie(settings.CSRF_COOKIE_NAME, path="/", domain=settings.COOKIE_DOMAIN)


def read_refresh_cookie(request: Request) -> str | None:
    return request.cookies.get(settings.REFRESH_COOKIE_NAME)


def verify_csrf(request: Request) -> None:
    """Double-submit check for cookie-authenticated endpoints (refresh, logout)."""
    cookie_token = request.cookies.get(settings.CSRF_COOKIE_NAME)
    header_token = request.headers.get("x-csrf-token")
    if not cookie_token or not header_token:
        raise Forbidden("Missing CSRF token.", code="csrf_missing")
    if not _equal(cookie_token, header_token):
        raise Forbidden("CSRF token mismatch.", code="csrf_invalid")


def _equal(a: str, b: str) -> bool:
    import hmac

    return hmac.compare_digest(a.encode(), b.encode())
