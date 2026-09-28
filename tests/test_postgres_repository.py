import uuid

import pytest
from sqlalchemy import text

from shared.db.session import session_scope
from shared.domain.models import Document
from shared.repositories.postgres import PostgresDocumentRegistory

pytestmark = pytest.mark.integration


@pytest.fixture
def tenant_id() -> str:
    tid = uuid.uuid4()
    with session_scope() as s:
        s.execute(
            text("INSERT INTO tenants (id, name, slug, plan) VALUES (:i, 'T', :s, 'standard')"),
            {"i": tid, "s": f"t-{tid.hex[:8]}"},
        )
    return str(tid)


def _doc(tenant_id: str, content_hash: str) -> Document:
    return Document(
        title="KYC Direction",
        source="RBI",
        source_url=f"https://rbi.org.in/{content_hash}",
        content="text",
        content_hash=content_hash,
        tenant_id=tenant_id,
    )


def test_saving_the_same_document_twice_is_idompotent(tenant_id: str) -> None:
    with session_scope() as s:
        repo = PostgresDocumentRegistory(s)
        first = repo.save(_doc(tenant_id, "HASH-1"))
        second = repo.save(_doc(tenant_id, "HASH-1"))
        assert first.id == second.id
        assert len(repo.list_current(tenant_id)) == 1


def test_another_tenant_cannot_read_the_document(tenant_id: str) -> None:
    other = str(uuid.uuid4())
    with session_scope() as s:
        repo = PostgresDocumentRegistory(s)
        saved = repo.save(_doc(tenant_id, "hash-2"))
        assert saved.id is not None
        assert repo.get(other, saved.id) is None
