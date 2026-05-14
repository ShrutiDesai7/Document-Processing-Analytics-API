from __future__ import annotations

from pydantic import BaseModel


class FrequentWord(BaseModel):
    word: str
    count: int


class DocumentAnalyzeResponse(BaseModel):
    document_id: str
    word_count: int
    sentence_count: int
    top_frequent_words: list[FrequentWord]
    estimated_reading_time_minutes: float

