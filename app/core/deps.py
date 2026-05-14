from __future__ import annotations

from app.core.config import Settings, get_settings
from app.database.session import get_db_session


def settings_dep() -> Settings:
    return get_settings()


async def db_session_dep():
    """
    Returns an AsyncSession when the DB is configured/initialized.
    Returns None when running without a database (e.g., local dev without MySQL, unit tests).
    """
    try:
        async for session in get_db_session():
            yield session
    except RuntimeError:
        yield None
