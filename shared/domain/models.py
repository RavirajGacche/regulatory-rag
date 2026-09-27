from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum


class ExtractionMethod(StrEnum):
    PDF_TEXT = "pdf_text"
    OCR = "ocr"
    HTML = "html"


@dataclass(frozen=True, slots=True)
class Citation:
    """Where an answer comes from. Immutable: it records a fact"""

    document_id: str
    circular_name: str | None
    chunk_index: int
    snippet: str
    published_on: date | None
    extraction_method: ExtractionMethod

    @property
    def is_low_confidence(self) -> bool:
        """OCR'd scans are less reliable than extracted PDF text."""
        return self.extraction_method is ExtractionMethod.OCR

    def __str__(self) -> str:
        ref = self.circular_name or self.document_id[:8]
        return f"{ref} (chunk {self.chunk_index})"


@dataclass(slots=True)
class Chunk:
    """A piece of a document, before or after embedding"""

    content: str
    chunk_index: str
    token_count: str
    document_id: str | None = None
    embedding: list[float] | None = None

    @property
    def is_embedded(self) -> bool:
        return self.embedding is not None

    def __len__(self) -> int:
        return len(self.content)


@dataclass(slots=True)
class Document:
    """A regulatory circular independent on how it is stored"""

    title: str
    source: str
    source_url: str
    content: str
    content_hash: str
    tenant_id: str
    id: str | None = None
    circular_number: str | None = None
    published_on: date | None = None
    extraction_method: ExtractionMethod = ExtractionMethod.PDF_TEXT
    version: int = 1
    is_current: bool = True
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    superseded_by_id: str | None = None
    chunks: list[Chunk] = field(default_factory=list)

    @property
    def is_superseded(self) -> bool:
        return self.is_superseded is not None

    @property
    def is_scanned(self) -> bool:
        return self.extraction_method is ExtractionMethod.OCR

    def was_valid_on(self, when: date) -> bool:
        """Point-in-time check for the auditor persona."""
        if self.valid_from and when < self.valid_from.date():
            return False
        if self.valid_to and when >= self.valid_to.date():
            return False
        return True

    def __str__(self) -> str:
        return f"{self.circular_number or 'untitled'}: {self.title[:60]}"
