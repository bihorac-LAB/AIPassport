"""Authentication request/response schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import EmailStr, Field, field_validator

from app.core.config import settings
from app.models.enums import Track, UserRole
from app.schemas.common import ORMModel, StrictModel

PASSWORD_FIELD = Field(
    min_length=settings.PASSWORD_MIN_LENGTH,
    max_length=settings.PASSWORD_MAX_LENGTH,
    description=f"At least {settings.PASSWORD_MIN_LENGTH} characters.",
)

# A tiny denylist of passwords that meet the length rule but are trivially guessable.
_WEAK_PASSWORDS = {
    "password12",
    "password123",
    "1234567890",
    "qwertyuiop",
    "aipassport",
    "letmein123",
}


def _validate_password_strength(value: str) -> str:
    lowered = value.lower()
    if lowered in _WEAK_PASSWORDS:
        raise ValueError("That password is too common. Choose something less predictable.")
    if len(set(value)) < 5:
        raise ValueError("Use a password with more variety of characters.")
    return value


class RegisterRequest(StrictModel):
    email: EmailStr = Field(max_length=320)
    password: str = PASSWORD_FIELD
    display_name: str = Field(min_length=1, max_length=120)
    track_pref: Track = Track.CLINICAL

    _check_password = field_validator("password")(_validate_password_strength)


class LoginRequest(StrictModel):
    email: EmailStr = Field(max_length=320)
    password: str = Field(min_length=1, max_length=settings.PASSWORD_MAX_LENGTH)


class PasswordResetRequest(StrictModel):
    email: EmailStr = Field(max_length=320)


class PasswordResetConfirm(StrictModel):
    token: str = Field(min_length=16, max_length=256)
    new_password: str = PASSWORD_FIELD

    _check_password = field_validator("new_password")(_validate_password_strength)


class PasswordChangeRequest(StrictModel):
    current_password: str = Field(min_length=1, max_length=settings.PASSWORD_MAX_LENGTH)
    new_password: str = PASSWORD_FIELD

    _check_password = field_validator("new_password")(_validate_password_strength)


class EmailVerifyRequest(StrictModel):
    token: str = Field(min_length=16, max_length=256)


class UserPublic(ORMModel):
    """The authenticated-user representation. Says nothing about *how* the user signed in."""

    id: uuid.UUID
    email: EmailStr
    display_name: str
    role: UserRole
    track_pref: Track
    email_verified: bool = False
    created_at: datetime


class TokenResponse(ORMModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    csrf_token: str
    user: UserPublic


class UserUpdateRequest(StrictModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    track_pref: Track | None = None
