import uuid
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backend.domain.models import ExtractedClaim
from backend.services.extractor import ClaimExtractionError
from main import app

client = TestClient(app)


def test_create_and_retrieve_document():
    # 1. Create a document
    payload = {
        "title": "API Specification v1",
        "content": "# Authentication\nAll requests require a bearer token.",
        "version": "1.0.0",
    }
    response = client.post("/api/v1/documents/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert "id" in data
    doc_id = data["id"]

    # 2. Retrieve the document by ID
    get_response = client.get(f"/api/v1/documents/{doc_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == doc_id
    assert get_data["title"] == payload["title"]

    # 3. List all documents
    list_response = client.get("/api/v1/documents/")
    assert list_response.status_code == 200
    docs = list_response.json()
    assert len(docs) >= 1


@patch(
    "backend.api.v1.documents.claim_extractor.extract_claims", new_callable=AsyncMock
)
def test_extract_claims(mock_extract):
    # 1. Create a document first
    payload = {
        "title": "OAuth Spec",
        "content": "The system must support OAuth 2.0. Passwords must be at least 12 characters long.",
        "version": "1.0.0",
    }
    response = client.post("/api/v1/documents/", json=payload)
    doc_id = response.json()["id"]

    # 2. Extraction is mocked deterministically -- tests must never depend on
    # a real, network-reachable LLM provider or a configured API key. Claim
    # ids are generated per test run (not hardcoded) because the app uses a
    # persistent, file-backed SQLite database, and a hardcoded id would
    # collide with a leftover row from a previous run of this same test.
    mock_extract.return_value = [
        ExtractedClaim(
            id=f"claim-oauth-1-{uuid.uuid4()}",
            document_id=doc_id,
            statement="The system must support OAuth 2.0.",
            section=None,
        ),
        ExtractedClaim(
            id=f"claim-oauth-2-{uuid.uuid4()}",
            document_id=doc_id,
            statement="Passwords must be at least 12 characters long.",
            section=None,
        ),
    ]

    extract_response = client.post(f"/api/v1/documents/{doc_id}/extract")
    assert extract_response.status_code == 200
    claims = extract_response.json()

    assert len(claims) == 2
    assert claims[0]["statement"] == "The system must support OAuth 2.0."
    assert claims[0]["document_id"] == doc_id
    mock_extract.assert_awaited_once()


@patch(
    "backend.api.v1.documents.claim_extractor.extract_claims", new_callable=AsyncMock
)
def test_extract_claims_returns_clean_error_when_provider_unavailable(mock_extract):
    payload = {
        "title": "Unreachable Provider Spec",
        "content": "Some requirement text.",
        "version": "1.0.0",
    }
    response = client.post("/api/v1/documents/", json=payload)
    doc_id = response.json()["id"]

    mock_extract.side_effect = ClaimExtractionError(
        "Claim extraction is not configured: GROQ_API_KEY is missing."
    )

    extract_response = client.post(f"/api/v1/documents/{doc_id}/extract")

    # A missing/misconfigured provider must surface as a clean, typed error
    # -- never an opaque 500, and never fabricated claims.
    assert extract_response.status_code == 503
    assert "GROQ_API_KEY" in extract_response.json()["detail"]


def test_extract_claims_404_for_missing_document():
    response = client.post("/api/v1/documents/does-not-exist/extract")
    assert response.status_code == 404


def test_get_document_404_for_missing_document():
    response = client.get("/api/v1/documents/does-not-exist")
    assert response.status_code == 404


def test_delete_document_404_for_missing_document():
    response = client.delete("/api/v1/documents/does-not-exist")
    assert response.status_code == 404
