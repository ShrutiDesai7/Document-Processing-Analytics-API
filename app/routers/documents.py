from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

import logging

from app.core.config import Settings
from app.core.deps import db_session_dep, settings_dep
from app.schemas.documents import DocumentUploadResponse
from app.schemas.analytics import DocumentAnalyzeResponse
from app.schemas.extraction import DocumentExtractResponse
from app.services.analytics_service import analyze_text
from app.services.extraction_service import (
    DocumentNotFoundError,
    ExtractionFailedError,
    UnsupportedDocumentTypeError,
    extract_text_for_document,
)
from app.services.file_service import (
    EmptyFileError,
    FileSaveError,
    InvalidFileExtensionError,
    save_document_upload,
)

router = APIRouter(prefix="/documents")
logger = logging.getLogger(__name__)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    settings: Settings = Depends(settings_dep),
    db: AsyncSession | None = Depends(db_session_dep),
) -> DocumentUploadResponse:
    try:
        return await save_document_upload(file=file, uploads_dir=settings.uploads_dir, db=db)
    except InvalidFileExtensionError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only .pdf and .txt files are supported.",
        ) from exc
    except EmptyFileError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty files are not allowed.",
        ) from exc
    except FileSaveError as exc:
        logger.exception("Upload failed for filename=%s", getattr(file, "filename", None))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file.",
        ) from exc


@router.post(
    "/{document_id}/extract",
    response_model=DocumentExtractResponse,
)
async def extract_document_text(
    document_id: str,
    settings: Settings = Depends(settings_dep),
) -> DocumentExtractResponse:
    try:
        return await extract_text_for_document(
            uploads_dir=settings.uploads_dir,
            document_id=document_id,
        )
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        ) from exc
    except UnsupportedDocumentTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported document type.",
        ) from exc
    except ExtractionFailedError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract text from document.",
        ) from exc


@router.post(
    "/{document_id}/analyze",
    response_model=DocumentAnalyzeResponse,
)
async def analyze_document(
    document_id: str,
    settings: Settings = Depends(settings_dep),
) -> DocumentAnalyzeResponse:
    try:
        extracted = await extract_text_for_document(
            uploads_dir=settings.uploads_dir,
            document_id=document_id,
        )
        return analyze_text(document_id=document_id, text=extracted.text)
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        ) from exc
    except UnsupportedDocumentTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported document type.",
        ) from exc
    except ExtractionFailedError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract text from document.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze document.",
        ) from exc
