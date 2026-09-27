from datetime import date
from uuid import uuid4

from shared.domain.models import Document


class FakeDocumentRepository:
    "In-memory document storage, for tests"

    def __init__(self) -> None:
        self._rows: dict[tuple[str, str], Document] = {}

    def get(self, tenant_id: str, document_id: str) -> Document | None:
        return self._rows.get((tenant_id, document_id))

    def get_by_content_hash(self, tenant_id: str, content_hash: str) -> Document | None:
        for (t, _), doc in self._rows.items():
            if t == tenant_id and doc.content_hash == content_hash:
                return doc
        return None

    def list_current(self, tenant_id: str, limit: int = 20) -> list[Document]:
        rows = [d for (t, _), d in self._rows.items() if t == tenant_id and d.is_current]
        rows.sort(key=lambda d: d.published_on or date.min, reverse=True)
        return rows[:limit]

    def save(self, document: Document) -> Document:
        existing = self.get_by_content_hash(document.tenant_id, document.content_hash)
        if existing is not None:
            return existing
        if document.id is None:
            document.id = str(uuid4())
        self._rows[(document.tenant_id, document.id)] = document
        return document
