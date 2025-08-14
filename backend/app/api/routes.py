from fastapi import APIRouter
from app.api.api_v1.endpoints import tasks, responses, votes, gallery, cache
from app.auth.routes import router as auth_router

api_router = APIRouter()

api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(responses.router, prefix="/responses", tags=["responses"])
api_router.include_router(votes.router, prefix="/votes", tags=["votes"])
api_router.include_router(gallery.router, prefix="/gallery", tags=["gallery"])
api_router.include_router(cache.router, prefix="/cache", tags=["cache"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])