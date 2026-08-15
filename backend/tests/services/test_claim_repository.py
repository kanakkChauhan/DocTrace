import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.domain.models import ExtractedClaim
from backend.infrastructure.claim_repository import ClaimRepository
from backend.infrastructure.database import Base


@pytest.fixture
def repo():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return ClaimRepository(db_session_factory=session_factory)


def test_save_and_get_claims_for_document(repo):
    claims = [
        ExtractedClaim(
            id="c1", document_id="doc-1", statement="Hash passwords.", section="Auth"
        ),
        ExtractedClaim(
            id="c2", document_id="doc-1", statement="Expire tokens.", section="Auth"
        ),
    ]
    repo.save_claims_for_document("doc-1", claims)

    fetched = repo.get_claims_for_document("doc-1")
    assert len(fetched) == 2
    ids = {c.id for c in fetched}
    assert ids == {"c1", "c2"}


def test_save_claims_replaces_previous_set(repo):
    first = [
        ExtractedClaim(
            id="c1", document_id="doc-1", statement="Old claim.", section=None
        )
    ]
    repo.save_claims_for_document("doc-1", first)

    second = [
        ExtractedClaim(
            id="c2", document_id="doc-1", statement="New claim.", section=None
        )
    ]
    repo.save_claims_for_document("doc-1", second)

    fetched = repo.get_claims_for_document("doc-1")
    assert len(fetched) == 1
    assert fetched[0].id == "c2"


def test_get_claims_for_document_empty(repo):
    assert repo.get_claims_for_document("nonexistent") == []


def test_get_by_id(repo):
    claim = ExtractedClaim(
        id="c1", document_id="doc-1", statement="Hash passwords.", section="Auth"
    )
    repo.save_claims_for_document("doc-1", [claim])

    fetched = repo.get_by_id("c1")
    assert fetched is not None
    assert fetched.statement == "Hash passwords."

    assert repo.get_by_id("missing") is None
