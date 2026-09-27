import pytest

from shared.domain.models import Document
from shared.repositories.fake import FakeDocumentRepository


def _doc(tenant: str, content_hash: str) -> Document:
    return Document(
        title="KYC Direction",
        source="RBI",
        source_url=f"https://rbi.org.in/{content_hash}",
        content="text",
        content_hash=content_hash,
        tenant_id=tenant,
    )


@pytest.fixture
def repo() -> FakeDocumentRepository:
    return FakeDocumentRepository()


def test_saved_document_can_be_read_back(repo: FakeDocumentRepository) -> None:
    saved = repo.save(_doc("t1", "h1"))
    assert saved.id is not None
    assert repo.get("t1", saved.id) == saved


def test_tenant_cannot_read_another_tenants_document(repo: FakeDocumentRepository) -> None:
    saved = repo.save(_doc("t1", "h1"))
    assert saved.id is not None
    assert repo.get("t2", saved.id) is None


def test_listing_only_return_your_own_documents(repo: FakeDocumentRepository) -> None:
    repo.save(_doc("t1", "h1"))
    repo.save(_doc("t1", "h2"))
    repo.save(_doc("t2", "h3"))
    assert len(repo.list_current("t1")) == 2
    assert len(repo.list_current("t2")) == 1


def test_saving_the_same_content_twice_creates_one_document(repo: FakeDocumentRepository) -> None:
    first = repo.save(_doc("t1", "same"))
    second = repo.save(_doc("t1", "same"))
    assert first.id == second.id
    assert len(repo.list_current("t1")) == 1
