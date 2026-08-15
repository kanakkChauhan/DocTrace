import uuid
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backend.domain.models import ExtractedClaim
from backend.infrastructure.claim_repository import claim_repository
from backend.services.extractor import ClaimExtractionError
from main import app

client = TestClient(app)


def _create_document(
    title="GitHub Trace Spec", content="The system must hash passwords securely."
):
    response = client.post(
        "/api/v1/documents/",
        json={"title": title, "content": content, "version": "1.0.0"},
    )
    assert response.status_code == 201
    return response.json()["id"]


@patch("backend.api.v1.trace.github_service.fetch_repository_files")
def test_trace_run_with_github_url_uses_fetched_files(mock_fetch):
    doc_id = _create_document()

    claim_repository.save_claims_for_document(
        doc_id,
        [
            ExtractedClaim(
                id=f"claim-github-1-{uuid.uuid4()}",
                document_id=doc_id,
                statement="Hash the password securely.",
                section=None,
            )
        ],
    )

    mock_fetch.return_value = [
        (
            "auth.py",
            (
                "def hash_password(password):\n"
                "    '''Hash password securely.'''\n"
                "    pass\n"
            ),
        )
    ]

    response = client.post(
        "/api/v1/trace/",
        json={"document_id": doc_id, "github_url": "https://github.com/test/repo"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_matches"] >= 1
    mock_fetch.assert_called_once_with("https://github.com/test/repo")


@patch("backend.api.v1.trace.github_service.fetch_repository_files")
def test_trace_run_with_invalid_github_url_returns_clean_400(mock_fetch):
    doc_id = _create_document()

    claim_repository.save_claims_for_document(
        doc_id,
        [
            ExtractedClaim(
                id=f"claim-github-2-{uuid.uuid4()}",
                document_id=doc_id,
                statement="Hash the password securely.",
                section=None,
            )
        ],
    )

    mock_fetch.side_effect = ValueError(
        "'not-a-repo' is not a valid GitHub repository URL."
    )

    response = client.post(
        "/api/v1/trace/",
        json={"document_id": doc_id, "github_url": "not-a-repo"},
    )

    assert response.status_code == 400
    assert "not a valid GitHub" in response.json()["detail"]


def test_trace_run_404_for_missing_document():
    response = client.post(
        "/api/v1/trace/",
        json={"document_id": "does-not-exist", "files": []},
    )
    assert response.status_code == 404


@patch("backend.api.v1.trace.claim_extractor.extract_claims", new_callable=AsyncMock)
def test_trace_run_returns_clean_error_when_claim_extraction_fallback_fails(
    mock_extract,
):
    doc_id = _create_document(
        title="No Claims Yet Spec", content="A brand-new spec with no saved claims."
    )

    mock_extract.side_effect = ClaimExtractionError(
        "Claim extraction is not configured: GROQ_API_KEY is missing."
    )

    response = client.post(
        "/api/v1/trace/",
        json={"document_id": doc_id, "files": []},
    )

    assert response.status_code == 503
    assert "GROQ_API_KEY" in response.json()["detail"]
