from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import anyio
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.schemas.documents import DocumentUploadResponse

import logging

logger = logging.getLogger(__name__)


ALLOWED_EXTENSIONS: set[str] = {".pdf", ".txt"}


class DocumentUploadError(Exception):
    pass


@dataclass(frozen=True)
class InvalidFileExtensionError(DocumentUploadError):
    filename: str


@dataclass(frozen=True)
class EmptyFileError(DocumentUploadError):
    filename: str


@dataclass(frozen=True)
class FileSaveError(DocumentUploadError):
    filename: str


def _get_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


async def _write_bytes(path: Path, data: bytes) -> None:
    def _sync_write() -> None:
        with path.open("ab") as f:
            f.write(data)

    await anyio.to_thread.run_sync(_sync_write)


async def save_document_upload(
    file: UploadFile,
    uploads_dir: str,
    db: AsyncSession | None = None,
    allowed_extensions: set[str] | None = None,
) -> DocumentUploadResponse:
    if not file.filename:
        raise InvalidFileExtensionError(filename="")

    ext = _get_extension(file.filename)
    allowed = allowed_extensions or ALLOWED_EXTENSIONS
    if ext not in allowed:
        raise InvalidFileExtensionError(filename=file.filename)

    base_dir = Path(uploads_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    document_id = str(uuid4())
    stored_filename = f"{document_id}{ext}"
    destination = base_dir / stored_filename

    size_bytes = 0
    try:
        first_chunk = await file.read(1024)
        if not first_chunk:
            raise EmptyFileError(filename=file.filename)

        await _write_bytes(destination, first_chunk)
        size_bytes += len(first_chunk)

        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            await _write_bytes(destination, chunk)
            size_bytes += len(chunk)
    except DocumentUploadError:
        try:
            destination.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    except Exception as exc:
        logger.exception(
            "Failed saving upload to disk: filename=%s destination=%s",
            file.filename,
            str(destination),
        )
        try:
            destination.unlink(missing_ok=True)
        except OSError:
            pass
        raise FileSaveError(filename=file.filename) from exc
    finally:
        await file.close()

    if db is not None:
        try:
            db.add(
                Document(
                    document_id=document_id,
                    original_filename=file.filename,
                    stored_filename=stored_filename,
                    content_type=file.content_type,
                    size_bytes=size_bytes,
                    relative_path=str(destination.as_posix()),
                )
            )
            await db.commit()
        except Exception as exc:
            logger.exception(
                "Failed persisting document metadata: document_id=%s filename=%s",
                document_id,
                file.filename,
            )
            try:
                await db.rollback()
            except Exception:
                pass
            try:
                destination.unlink(missing_ok=True)
            except OSError:
                pass
            raise FileSaveError(filename=file.filename) from exc

    return DocumentUploadResponse(
        document_id=document_id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        content_type=file.content_type,
        size_bytes=size_bytes,
        relative_path=str(destination.as_posix()),
    )
