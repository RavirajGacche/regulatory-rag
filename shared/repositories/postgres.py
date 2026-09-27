from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.db.models import Document as DocumentRow
from shared.domain.models import Document, ExtractionMethod


def _to_domain(row: DocumentRow) -> Document:
    """Convert a database row into a plain domain object."""

    return Document(
        id=str(row.id),
        tenant_id=str(row.tenant_id),
        title=row.title,
        source=row.source,
        source_url=row.source_url,
        content="",
        content_hash=row.content_hash,
        circular_number=row.circular_number,
        published_on=row.published_on,
        extraction_method=ExtractionMethod(row.extraction_method),
        version=row.version,
        is_current=row.is_current,
        valid_from=row.valid_from,
        valid_to=row.valid_to,
        superseded_by_id=str(row.superseded_by_id) if row.superseded_by_id else None,
    )


class PostgresDocumentRegistory:
    """All document queries live here. Every one is scoped to a tenant"""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, tenant_id: str, document_id: str) -> Document | None:
        stmt = select(DocumentRow).where(
            DocumentRow.tenant_id == UUID(tenant_id),
            DocumentRow.id == UUID(document_id),
            DocumentRow.deleted_at.is_(None),
        )
        row = self._session.scalars(stmt).one_or_none()
        return _to_domain(row) if row else None

    def get_by_content_hash(self, tenant_id: str, content_hash: str) -> Document | None:
        stmt = select(DocumentRow).where(
            DocumentRow.tenant_id == UUID(tenant_id), DocumentRow.content_hash == content_hash
        )
        row = self._session.scalars(stmt).one_or_none()
        return _to_domain(row) if row else None

    def list_current(self, tenant_id: str, limit: int = 20) -> list[Document]:
        stmt = (
            select(DocumentRow)
            .where(
                DocumentRow.tenant_id == UUID(tenant_id),
                DocumentRow.is_current.is_(True),
                DocumentRow.deleted_at.is_(None),
            )
            .order_by(DocumentRow.published_on.desc())
            .limit(limit)
        )
        return [_to_domain(row) for row in self._session.scalars(stmt)]

    def save(self, document: Document) -> Document:
        raise NotImplementedError("S12: upsert with on Conflict")
