from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse


def build_frontend_router(frontend_dir: str = "frontend") -> APIRouter:
    router = APIRouter(include_in_schema=False)
    index_path = Path(frontend_dir) / "index.html"

    @router.get("/")
    async def serve_index() -> FileResponse:
        return FileResponse(index_path)

    return router

