from typing import Protocol

from shared.domain.models import Document


class DocumentRepository(Protocol):
    """The methods any document repository must provide. Checked by mypy only"""

    def get(self, tenant_id: str, document_id: str) -> Document | None: ...

    def get_by_content_hash(self, tenant_id: str, content_hash: str) -> Document | None: ...

    def list_current(self, tenant_id: str, limit: int = 20) -> list[Document]: ...

    def save(self, document: Document) -> Document: ...
