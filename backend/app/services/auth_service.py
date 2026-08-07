"""Registration, login, refresh rotation, logout, password reset, email verification."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import (
    BadRequest,
    EmailAlreadyRegistered,
    InvalidCredentials,
    Unauthorized,
)
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    email_log_id,
    hash_identifier,
    hash_password,
    hash_token,
    needs_rehash,
    new_csrf_token,
    new_opaque_token,
    verify_password,
)
from app.models import (
    AuthSession,
    EmailVerificationToken,
    IdentityProvider,
    PasswordResetToken,
    Track,
    User,
    UserIdentity,
    UserRole,
)

log = get_logger("aipassport.auth")


class IssuedSession:
    __slots__ = ("access_token", "expires_in", "refresh_token", "refresh_max_age", "csrf_token")

    def __init__(
        self,
        access_token: str,
        expires_in: int,
        refresh_token: str,
        refresh_max_age: int,
        csrf_token: str,
    ) -> None:
        self.access_token = access_token
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self.refresh_max_age = refresh_max_age
        self.csrf_token = csrf_token


def normalize_email(email: str) -> str:
    return email.strip().lower()


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Lookup ──────────────────────────────────────────────────────────────

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(func.lower(User.email) == normalize_email(email))
        return (await self.db.execute(stmt)).scalar_one_or_none()

    # ── Registration ────────────────────────────────────────────────────────

    async def register(
        self,
        *,
        email: str,
        password: str,
        display_name: str,
        track_pref: Track,
        user_agent: str | None,
        ip: str | None,
    ) -> tuple[User, IssuedSession]:
        normalized = normalize_email(email)
        if await self.get_user_by_email(normalized) is not None:
            raise EmailAlreadyRegistered()

        user = User(
            email=normalized,
            display_name=display_name.strip(),
            role=UserRole.LEARNER.value,
            track_pref=track_pref.value,
            is_active=True,
        )
        self.db.add(user)
        await self.db.flush()

        identity = UserIdentity(
            user_id=user.id,
            provider=IdentityProvider.LOCAL.value,
            provider_subject=normalized,
            password_hash=hash_password(password),
            email_verified=False,
            last_login_at=datetime.now(UTC),
        )
        self.db.add(identity)
        await self.db.flush()

        issued = await self._create_session(user, user_agent=user_agent, ip=ip)
        await self.db.commit()
        await self.db.refresh(user)
        log.info("user_registered", user_id=str(user.id))
        return user, issued

    # ── Login ───────────────────────────────────────────────────────────────

    async def login(
        self, *, email: str, password: str, user_agent: str | None, ip: str | None
    ) -> tuple[User, IssuedSession]:
        user = await self.get_user_by_email(email)
        identity = user.local_identity if user else None
        password_hash = identity.password_hash if identity else None

        # Always runs a verification (dummy hash when the account does not exist) so response
        # timing does not reveal whether the email is registered.
        if not verify_password(password, password_hash) or user is None or identity is None:
            log.info("login_failed", email_tag=email_log_id(email))
            raise InvalidCredentials()

        if not user.is_active:
            raise Unauthorized("Account is disabled.", code="account_inactive")

        if needs_rehash(identity.password_hash or ""):
            identity.password_hash = hash_password(password)

        identity.last_login_at = datetime.now(UTC)
        issued = await self._create_session(user, user_agent=user_agent, ip=ip)
        await self.db.commit()
        await self.db.refresh(user)
        log.info("login_succeeded", user_id=str(user.id))
        return user, issued

    # ── Sessions ────────────────────────────────────────────────────────────

    async def _create_session(
        self,
        user: User,
        *,
        user_agent: str | None,
        ip: str | None,
        family_id: uuid.UUID | None = None,
    ) -> IssuedSession:
        refresh_token = new_opaque_token()
        expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        session_id = uuid.uuid4()
        auth_session = AuthSession(
            id=session_id,
            user_id=user.id,
            family_id=family_id or session_id,
            refresh_token_hash=hash_token(refresh_token),
            expires_at=expires_at,
            user_agent=user_agent,
            ip_hash=hash_identifier(ip) if ip else None,
            last_used_at=datetime.now(UTC),
        )
        self.db.add(auth_session)
        await self.db.flush()

        access_token, access_expires = create_access_token(
            user_id=user.id, session_id=session_id, role=user.role
        )
        return IssuedSession(
            access_token=access_token,
            expires_in=int((access_expires - datetime.now(UTC)).total_seconds()),
            refresh_token=refresh_token,
            refresh_max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86_400,
            csrf_token=new_csrf_token(),
        )

    async def refresh(
        self, *, refresh_token: str, user_agent: str | None, ip: str | None
    ) -> tuple[User, IssuedSession]:
        token_hash = hash_token(refresh_token)
        stmt = select(AuthSession).where(AuthSession.refresh_token_hash == token_hash)
        session = (await self.db.execute(stmt)).scalar_one_or_none()
        if session is None:
            raise Unauthorized("Session not recognized.", code="invalid_refresh")

        now = datetime.now(UTC)

        # Reuse detection: a token that has already been rotated means the cookie leaked.
        if session.rotated_to_id is not None:
            await self._revoke_family(session.family_id)
            await self.db.commit()
            log.warning(
                "refresh_reuse_detected", user_id=str(session.user_id), family=str(session.family_id)
            )
            raise Unauthorized("Session revoked for security reasons.", code="refresh_reuse")

        if session.revoked_at is not None or session.expires_at <= now:
            raise Unauthorized("Session has expired.", code="refresh_expired")

        user = await self.db.get(User, session.user_id)
        if user is None or not user.is_active:
            raise Unauthorized("Account is not available.", code="account_inactive")

        issued = await self._create_session(
            user, user_agent=user_agent, ip=ip, family_id=session.family_id
        )
        # Mark the presented token rotated, pointing at its replacement.
        new_session = (
            await self.db.execute(
                select(AuthSession)
                .where(AuthSession.family_id == session.family_id)
                .order_by(AuthSession.created_at.desc())
                .limit(1)
            )
        ).scalar_one()
        session.rotated_to_id = new_session.id
        session.revoked_at = now
        await self.db.commit()
        await self.db.refresh(user)
        return user, issued

    async def logout(self, *, refresh_token: str | None, user_id: uuid.UUID | None) -> None:
        now = datetime.now(UTC)
        if refresh_token:
            stmt = select(AuthSession).where(
                AuthSession.refresh_token_hash == hash_token(refresh_token)
            )
            session = (await self.db.execute(stmt)).scalar_one_or_none()
            if session is not None and session.revoked_at is None:
                session.revoked_at = now
        elif user_id is not None:
            await self._revoke_all(user_id)
        await self.db.commit()

    async def logout_all(self, user_id: uuid.UUID) -> None:
        await self._revoke_all(user_id)
        await self.db.commit()

    async def _revoke_all(self, user_id: uuid.UUID) -> None:
        await self.db.execute(
            update(AuthSession)
            .where(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )

    async def _revoke_family(self, family_id: uuid.UUID) -> None:
        await self.db.execute(
            update(AuthSession)
            .where(AuthSession.family_id == family_id, AuthSession.revoked_at.is_(None))
            .values(revoked_at=datetime.now(UTC))
        )

    # ── Password management ─────────────────────────────────────────────────

    async def change_password(
        self, *, user: User, current_password: str, new_password: str
    ) -> None:
        identity = user.local_identity
        if identity is None or not verify_password(current_password, identity.password_hash):
            raise InvalidCredentials("Current password is incorrect.")
        identity.password_hash = hash_password(new_password)
        await self._revoke_all(user.id)
        await self.db.commit()
        log.info("password_changed", user_id=str(user.id))

    async def create_password_reset(self, email: str) -> str | None:
        """Returns the token when the account exists; callers must not vary their response."""
        user = await self.get_user_by_email(email)
        if user is None or user.local_identity is None:
            log.info("password_reset_unknown_account", email_tag=email_log_id(email))
            return None
        token = new_opaque_token()
        self.db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hash_token(token),
                expires_at=datetime.now(UTC)
                + timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES),
            )
        )
        await self.db.commit()
        log.info("password_reset_issued", user_id=str(user.id))
        return token

    async def confirm_password_reset(self, *, token: str, new_password: str) -> None:
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == hash_token(token)
        )
        record = (await self.db.execute(stmt)).scalar_one_or_none()
        now = datetime.now(UTC)
        if record is None or record.used_at is not None or record.expires_at <= now:
            raise BadRequest("This reset link is invalid or has expired.", code="reset_invalid")

        user = await self.db.get(User, record.user_id)
        if user is None:
            raise BadRequest("This reset link is invalid or has expired.", code="reset_invalid")
        identity = user.local_identity
        if identity is None:
            raise BadRequest("This account cannot reset a password.", code="reset_invalid")

        identity.password_hash = hash_password(new_password)
        record.used_at = now
        await self._revoke_all(user.id)
        await self.db.commit()
        log.info("password_reset_completed", user_id=str(user.id))

    # ── Email verification ──────────────────────────────────────────────────

    async def create_email_verification(self, user: User) -> str:
        token = new_opaque_token()
        self.db.add(
            EmailVerificationToken(
                user_id=user.id,
                token_hash=hash_token(token),
                expires_at=datetime.now(UTC)
                + timedelta(hours=settings.EMAIL_VERIFY_EXPIRE_HOURS),
            )
        )
        await self.db.commit()
        return token

    async def confirm_email_verification(self, token: str) -> None:
        stmt = select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == hash_token(token)
        )
        record = (await self.db.execute(stmt)).scalar_one_or_none()
        now = datetime.now(UTC)
        if record is None or record.used_at is not None or record.expires_at <= now:
            raise BadRequest(
                "This verification link is invalid or has expired.", code="verify_invalid"
            )
        user = await self.db.get(User, record.user_id)
        if user is None:
            raise BadRequest("This verification link is invalid.", code="verify_invalid")
        identity = user.local_identity
        if identity is not None:
            identity.email_verified = True
        record.used_at = now
        await self.db.commit()
