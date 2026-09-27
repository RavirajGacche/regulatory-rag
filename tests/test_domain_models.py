import dataclasses
from datetime import UTC, date, datetime

import pytest

from shared.domain.models import Chunk, Citation, Document, ExtractionMethod


def _doc(**kwargs:object) -> Document:
    base = dict(
        title="KYC Master Direction",
        source="RBI",
        source_url="https://rbi.org.in/x",
        content="text",
        content_hash="a"*64,
        tenant_id="t1"
    )
    return Document(**{**base, **kwargs}) #type ignore[arg-type]


def test_citation_is_immutable() -> None:
    c = Citation("d1", "RBI/1", 0, "s", date(2025, 1, 1), ExtractionMethod.PDF_TEXT)
    with pytest.raises(dataclasses.FrozenInstanceError):
        c.chunk_index = 5

def test_equal_citations_duplicate_in_a_set() -> None:
    args = ("d1", "RBI/1", 0, "s", date(2025, 1, 1), ExtractionMethod.PDF_TEXT)
    assert len({Citation(*args), Citation(*args)}) == 1

def test_ocr_citation_flagged_low_confidence() -> None:
    c = Citation("d1", None, 0, "s", None, ExtractionMethod.OCR)
    assert c.is_low_confidence

def test_was_valid_on_respects_the_validity_window() -> None:
    doc = _doc(valid_from=datetime(2025, 1, 1, tzinfo=UTC), 
               valid_to=datetime(2025, 6, 1, tzinfo=UTC)
               )
    assert doc.was_valid_on(date(2025, 3, 1))
    assert not doc.was_valid_on(date(2024, 12, 31))
    assert not doc.was_valid_on(date(2025, 6, 1))  #valid_to is exclusive

def test_chunk_length_is_its_content_length() -> None:
    assert len(Chunk(content="Hello", chunk_index=0, token_count=1)) == 5