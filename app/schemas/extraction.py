from __future__ import annotations

from pydantic import BaseModel


class DocumentExtractResponse(BaseModel):
    document_id: str
    file_type: str
    character_count: int
    preview: str
    text: str

