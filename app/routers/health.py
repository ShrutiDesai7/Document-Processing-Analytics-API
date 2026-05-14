from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.config import Settings
from app.core.deps import settings_dep
from app.schemas.health import HealthResponse
from app.services.health_service import get_health

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(settings_dep)) -> HealthResponse:
    return get_health(settings)
