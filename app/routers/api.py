from __future__ import annotations

from fastapi import APIRouter

from app.routers.documents import router as documents_router
from app.routers.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(documents_router, tags=["documents"])
