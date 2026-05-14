from __future__ import annotations

from app.core.config import Settings
from app.schemas.health import HealthResponse


def get_health(settings: Settings) -> HealthResponse:
    return HealthResponse(status="ok", environment=settings.environment)

