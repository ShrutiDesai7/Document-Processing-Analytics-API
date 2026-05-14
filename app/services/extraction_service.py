from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import anyio
import pdfplumber

from app.schemas.extraction import DocumentExtractResponse


class DocumentExtractionError(Exception):
    pass


@dataclass(frozen=True)
class DocumentNotFoundError(DocumentExtractionError):
    document_id: str


@dataclass(frozen=True)
class UnsupportedDocumentTypeError(DocumentExtractionError):
    filename: str


@dataclass(frozen=True)
class ExtractionFailedError(DocumentExtractionError):
    filename: str


def _find_document_path(uploads_dir: str, document_id: str) -> Path:
    base_dir = Path(uploads_dir)
    if not base_dir.exists():
        raise DocumentNotFoundError(document_id=document_id)

    matches = list(base_dir.glob(f"{document_id}.*"))
    if not matches:
        raise DocumentNotFoundError(document_id=document_id)
    return matches[0]


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_pdf(path: Path) -> str:
    with pdfplumber.open(path) as pdf:
        parts: list[str] = []
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts).strip()


async def extract_text_for_document(
    *,
    uploads_dir: str,
    document_id: str,
    preview_chars: int = 200,
) -> DocumentExtractResponse:
    path = _find_document_path(uploads_dir, document_id)
    ext = path.suffix.lower()

    if ext == ".txt":
        file_type = "txt"
        extractor = _read_txt
    elif ext == ".pdf":
        file_type = "pdf"
        extractor = _read_pdf
    else:
        raise UnsupportedDocumentTypeError(filename=path.name)

    try:
        text = await anyio.to_thread.run_sync(extractor, path)
    except DocumentExtractionError:
        raise
    except Exception as exc:
        raise ExtractionFailedError(filename=path.name) from exc

    character_count = len(text)
    preview = text[:preview_chars]
    return DocumentExtractResponse(
        document_id=document_id,
        file_type=file_type,
        character_count=character_count,
        preview=preview,
        text=text,
    )

