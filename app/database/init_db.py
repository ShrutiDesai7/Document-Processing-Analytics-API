from __future__ import annotations

from sqlalchemy import text

from app.database.base import Base
from app.database import session as db_session


async def init_db() -> None:
    if db_session.engine is None:
        raise RuntimeError("Database engine is not initialized.")

    # Ensure models are imported so Base.metadata is populated.
    from app.models import document as _document  # noqa: F401

    async with db_session.engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
        await conn.run_sync(Base.metadata.create_all)
