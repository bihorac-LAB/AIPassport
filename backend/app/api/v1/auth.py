"""Authentication routes."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response, status

from app.auth.cookies import (
    clear_auth_cookies,
    read_refresh_cookie,
    set_csrf_cookie,
    set_refresh_cookie,
    verify_csrf,
)
from app.auth.dependencies import CurrentUser, DbSession, request_user_agent
from app.auth.rate_limit import client_ip, limiter
from app.core.config import settings
from app.core.errors import Unauthorized
from app.core.logging import get_logger
from app.core.security import email_log_id
from app.models import User
from app.schemas.auth import (
    EmailVerifyRequest,
    LoginRequest,
    PasswordChangeRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService, IssuedSession

router = APIRouter(prefix="/auth", tags=["auth"])
log = get_logger("aipassport.auth.api")


def _user_public(user: User) -> UserPublic:
    identity = user.local_identity
    return UserPublic(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        track_pref=user.track_pref,
        email_verified=bool(identity.email_verified) if identity else False,
        created_at=user.created_at,
    )


def _issue(response: Response, user: User, issued: IssuedSession) -> TokenResponse:
    set_refresh_cookie(response, issued.refresh_token, issued.refresh_max_age)
    set_csrf_cookie(response, issued.csrf_token, issued.refresh_max_age)
    return TokenResponse(
        access_token=issued.access_token,
        expires_in=issued.expires_in,
        csrf_token=issued.csrf_token,
        user=_user_public(user),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    db: DbSession,
) -> TokenResponse:
    ip = client_ip(request)
    limiter.check(
        "register:ip", ip, limit=settings.RATE_LIMIT_REGISTER_PER_HOUR, window_seconds=3600
    )

    service = AuthService(db)
    user, issued = await service.register(
        email=payload.email,
        password=payload.password,
        display_name=payload.display_name,
        track_pref=payload.track_pref,
        user_agent=request_user_agent(request),
        ip=ip,
    )
    # Email verification is issued immediately; delivery is a no-op until SMTP is configured.
    token = await service.create_email_verification(user)
    if not settings.SMTP_HOST:
        log.debug("email_verification_token_generated", user_id=str(user.id), token_len=len(token))
    return _issue(response, user, issued)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: DbSession,
) -> TokenResponse:
    ip = client_ip(request)
    window = settings.RATE_LIMIT_LOGIN_WINDOW_SECONDS
    limiter.check("login:ip", ip, limit=settings.RATE_LIMIT_LOGIN_PER_IP, window_seconds=window)
    limiter.check(
        "login:email",
        email_log_id(payload.email),
        limit=settings.RATE_LIMIT_LOGIN_PER_EMAIL,
        window_seconds=window,
    )

    user, issued = await AuthService(db).login(
        email=payload.email,
        password=payload.password,
        user_agent=request_user_agent(request),
        ip=ip,
    )
    return _issue(response, user, issued)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, response: Response, db: DbSession) -> TokenResponse:
    verify_csrf(request)
    token = read_refresh_cookie(request)
    if not token:
        raise Unauthorized("No active session.", code="no_refresh_cookie")

    ip = client_ip(request)
    limiter.check("refresh:ip", ip, limit=120, window_seconds=3600)

    try:
        user, issued = await AuthService(db).refresh(
            refresh_token=token, user_agent=request_user_agent(request), ip=ip
        )
    except Unauthorized:
        clear_auth_cookies(response)
        raise
    return _issue(response, user, issued)


@router.post("/logout", response_model=MessageResponse)
async def logout(request: Request, response: Response, db: DbSession) -> MessageResponse:
    verify_csrf(request)
    token = read_refresh_cookie(request)
    await AuthService(db).logout(refresh_token=token, user_id=None)
    clear_auth_cookies(response)
    return MessageResponse(detail="Signed out.")


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all(
    request: Request, response: Response, db: DbSession, user: CurrentUser
) -> MessageResponse:
    verify_csrf(request)
    await AuthService(db).logout_all(user.id)
    clear_auth_cookies(response)
    return MessageResponse(detail="Signed out of all devices.")


@router.post("/password/change", response_model=MessageResponse)
async def change_password(
    payload: PasswordChangeRequest,
    request: Request,
    response: Response,
    db: DbSession,
    user: CurrentUser,
) -> MessageResponse:
    limiter.check("password_change:user", str(user.id), limit=5, window_seconds=3600)
    await AuthService(db).change_password(
        user=user,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    clear_auth_cookies(response)
    return MessageResponse(detail="Password updated. Please sign in again.")


@router.post("/password-reset/request", response_model=MessageResponse)
async def request_password_reset(
    payload: PasswordResetRequest, request: Request, db: DbSession
) -> MessageResponse:
    limiter.check("reset:ip", client_ip(request), limit=10, window_seconds=3600)
    limiter.check("reset:email", email_log_id(payload.email), limit=3, window_seconds=3600)

    token = await AuthService(db).create_password_reset(payload.email)
    if token and not settings.SMTP_HOST:
        # Development affordance: without SMTP the flow is still testable from the log.
        log.debug("password_reset_token_generated", token_len=len(token))
    # Identical response whether or not the account exists — no enumeration.
    return MessageResponse(
        detail="If an account exists for that address, a reset link has been sent."
    )


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    payload: PasswordResetConfirm, request: Request, db: DbSession
) -> MessageResponse:
    limiter.check("reset_confirm:ip", client_ip(request), limit=20, window_seconds=3600)
    await AuthService(db).confirm_password_reset(
        token=payload.token, new_password=payload.new_password
    )
    return MessageResponse(detail="Password updated. You can now sign in.")


@router.post("/verify-email/request", response_model=MessageResponse)
async def request_email_verification(
    db: DbSession, user: CurrentUser
) -> MessageResponse:
    limiter.check("verify_request:user", str(user.id), limit=5, window_seconds=3600)
    token = await AuthService(db).create_email_verification(user)
    if not settings.SMTP_HOST:
        log.debug("email_verification_token_generated", user_id=str(user.id), token_len=len(token))
    return MessageResponse(detail="Verification email sent.")


@router.post("/verify-email/confirm", response_model=MessageResponse)
async def confirm_email_verification(
    payload: EmailVerifyRequest, db: DbSession
) -> MessageResponse:
    await AuthService(db).confirm_email_verification(payload.token)
    return MessageResponse(detail="Email verified.")
