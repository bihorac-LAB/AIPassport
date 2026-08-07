"""Current-user profile."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import _user_public
from app.auth.dependencies import CurrentUser, DbSession
from app.schemas.auth import UserPublic, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def read_me(user: CurrentUser) -> UserPublic:
    return _user_public(user)


@router.patch("/me", response_model=UserPublic)
async def update_me(
    payload: UserUpdateRequest, db: DbSession, user: CurrentUser
) -> UserPublic:
    if payload.display_name is not None:
        user.display_name = payload.display_name
    if payload.track_pref is not None:
        user.track_pref = payload.track_pref.value
    await db.commit()
    await db.refresh(user)
    return _user_public(user)
