from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from app.schemas.analytics import DocumentAnalyzeResponse, FrequentWord


class DocumentAnalyticsError(Exception):
    pass


@dataclass(frozen=True)
class AnalyticsFailedError(DocumentAnalyticsError):
    document_id: str


_WORD_RE = re.compile(r"[A-Za-z0-9']+")
_SENTENCE_RE = re.compile(r"[.!?]+")


def _normalize_word(word: str) -> str:
    return word.strip("'").lower()


def analyze_text(*, document_id: str, text: str, top_n: int = 8) -> DocumentAnalyzeResponse:
    words = [_normalize_word(w) for w in _WORD_RE.findall(text)]
    words = [w for w in words if w]
    word_count = len(words)

    sentence_count = len([m for m in _SENTENCE_RE.findall(text)])

    counts = Counter(words)
    top = [FrequentWord(word=w, count=c) for (w, c) in counts.most_common(top_n)]

    # Simple heuristic: 200 words per minute.
    estimated = round(word_count / 200.0, 2)

    return DocumentAnalyzeResponse(
        document_id=document_id,
        word_count=word_count,
        sentence_count=sentence_count,
        top_frequent_words=top,
        estimated_reading_time_minutes=estimated,
    )

