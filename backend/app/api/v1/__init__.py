from fastapi import APIRouter

from app.api.v1 import admin, ai, auth, events, health, modules, progress, responses, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(modules.router)
api_router.include_router(progress.router)
api_router.include_router(responses.router)
api_router.include_router(events.router)
api_router.include_router(ai.router)
api_router.include_router(admin.router)

__all__ = ["api_router", "health"]
