from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.core.deps import settings_dep
from app.main import create_app


@pytest.fixture()
def app():
    uploads_dir = Path("uploads") / "_test"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    test_settings = Settings.model_validate(
        {
            "UPLOADS_DIR": str(uploads_dir),
            "ENABLE_DOCS": False,
            "ENVIRONMENT": "test",
        }
    )

    fastapi_app = create_app()
    fastapi_app.dependency_overrides[settings_dep] = lambda: test_settings
    yield fastapi_app

    for path in uploads_dir.glob("*"):
        try:
            path.unlink()
        except OSError:
            pass


@pytest.mark.asyncio
async def test_upload_rejects_invalid_extension(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("malware.exe", b"nope", "application/octet-stream")},
        )
    assert resp.status_code == 415


@pytest.mark.asyncio
async def test_upload_rejects_empty_file(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("empty.txt", b"", "text/plain")},
        )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_upload_and_extract_txt(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        upload = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("hello.txt", b"hello world", "text/plain")},
        )

        assert upload.status_code == 201, upload.text
        payload = upload.json()
        assert payload["original_filename"] == "hello.txt"
        assert payload["stored_filename"].endswith(".txt")
        assert payload["size_bytes"] == 11

        stored_path = Path(payload["relative_path"])
        assert stored_path.exists()
        assert stored_path.read_text(encoding="utf-8") == "hello world"

        document_id = payload["document_id"]
        extract = await client.post(f"/api/v1/documents/{document_id}/extract")
        assert extract.status_code == 200, extract.text

        extracted = extract.json()
        assert extracted["document_id"] == document_id
        assert extracted["file_type"] == "txt"
        assert extracted["character_count"] == 11
        assert extracted["preview"] == "hello world"
        assert extracted["text"] == "hello world"
