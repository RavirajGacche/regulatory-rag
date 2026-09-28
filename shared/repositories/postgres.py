from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
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

        values = {
            "id": UUID(document.id) if document.id else uuid4(),
            "tenant_id": UUID(document.tenant_id),
            "source": document.source,
            "source_url": document.source_url,
            "title": document.title,
            "circular_number": document.circular_number,
            "published_on": document.published_on,
            "content_hash": document.content_hash,
            "extraction_method": str(document.extraction_method),
            "version": document.version,
            "is_current": document.is_current,
            "valid_from": document.valid_from or datetime.now(UTC),
        }

        stmt = (
            pg_insert(DocumentRow)
            .values(**values)
            .on_conflict_do_nothing(constraint="uq_doc_tenant_content_hash")
            .returning(DocumentRow.id)
        )

        inserted_id = self._session.scalars(stmt).one_or_none()
        self._session.commit()

        if inserted_id is None:
            existing = self.get_by_content_hash(document.tenant_id, document.content_hash)
            if existing is None:
                raise RuntimeError("Conflict reported but no existing row found")
            return existing

        document.id = str(inserted_id)
        return document
