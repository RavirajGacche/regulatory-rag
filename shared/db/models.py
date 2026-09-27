import uuid
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.db.base import Base, CreatedAtMixin, TimeStampMixin


class Tenant(Base, TimeStampMixin):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    plan: Mapped[str] = mapped_column(String(200), nullable=False, default="standard")

    documents: Mapped[list["Document"]] = relationship(back_populates="tenant")


class Document(Base, TimeStampMixin):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(String(40), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    circular_number: Mapped[str | None] = mapped_column(String(200))
    published_on: Mapped[date | None] = mapped_column(Date)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_document_id: Mapped[str | None] = mapped_column(String(48))
    extraction_method: Mapped[str] = mapped_column(String(20), nullable=False, default="pdf_text")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    superseded_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("documents.id"))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    tenant: Mapped["Tenant"] = relationship(back_populates="documents")
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("tenant_id", "source_url", "version", name="uq_doc_tenant_url_version"),
        UniqueConstraint("tenant_id", "content_hash", name="uq_doc_tenant_content_hash"),
        Index("ix_doc_tenant_published", "tenant_id", "published_on"),
        Index("ix_doc_tenant_current", "tenant_id", postgresql_where="is_current"),
    )


class Chunk(Base, CreatedAtMixin):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    document: Mapped["Document"] = relationship(back_populates="chunks")

    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_chunk_doc_index"),
        Index("ix_chunk_tenant_doc", "tenant_id", "document_id"),
    )
