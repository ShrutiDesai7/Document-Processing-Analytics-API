from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings

engine: AsyncEngine | None = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None


async def connect(settings: Settings) -> None:
    global engine, SessionLocal
    if engine is not None and SessionLocal is not None:
        return

    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def disconnect() -> None:
    global engine, SessionLocal
    if engine is None:
        return
    await engine.dispose()
    engine = None
    SessionLocal = None


async def get_db_session() -> AsyncIterator[AsyncSession]:
    if SessionLocal is None:
        raise RuntimeError("Database is not initialized. Did you call connect()?")
    async with SessionLocal() as session:
        yield session

