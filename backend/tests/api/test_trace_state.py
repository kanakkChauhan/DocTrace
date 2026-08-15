import uuid

from fastapi.testclient import TestClient

from backend.domain.models import ExtractedClaim
from backend.infrastructure.claim_repository import claim_repository
from main import app

client = TestClient(app)


def _create_document(
    title="Auth Spec", content="The system must hash passwords securely."
):
    response = client.post(
        "/api/v1/documents/",
        json={"title": title, "content": content, "version": "1.0.0"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_trace_state_empty_for_fresh_document():
    doc_id = _create_document()

    response = client.get(f"/api/v1/trace/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == doc_id
    assert data["total_claims"] == 0
    assert data["total_matches"] == 0
    assert data["claims"] == []
    assert data["links"] == []


def test_trace_state_404_for_missing_document():
    response = client.get("/api/v1/trace/does-not-exist")
    assert response.status_code == 404


def test_trace_run_uses_persisted_claims_and_survives_reload():
    doc_id = _create_document()

    # Seed claims directly, bypassing the live LLM call, so claim ids are
    # known ahead of time. Ids are generated per test run rather than
    # hardcoded, since the app uses a persistent (file-backed) SQLite
    # database and a hardcoded id would collide with leftover rows from a
    # previous test run.
    claim_id = f"claim-hash-password-{uuid.uuid4()}"
    seeded_claims = [
        ExtractedClaim(
            id=claim_id,
            document_id=doc_id,
            statement="Hash the password securely.",
            section=None,
        )
    ]
    claim_repository.save_claims_for_document(doc_id, seeded_claims)

    trace_response = client.post(
        "/api/v1/trace/",
        json={
            "document_id": doc_id,
            "files": [
                {
                    "filepath": "auth.py",
                    "source_code": (
                        "def hash_password(password):\n"
                        "    '''Hash password securely.'''\n"
                        "    pass\n"
                    ),
                }
            ],
        },
    )
    assert trace_response.status_code == 200
    trace_data = trace_response.json()

    assert trace_data["total_claims"] == 1
    assert trace_data["total_matches"] >= 1
    assert trace_data["claims"][0]["id"] == claim_id

    matched_link = next(
        link for link in trace_data["links"] if link["claim_id"] == claim_id
    )
    link_id = matched_link["id"]

    status_response = client.patch(
        f"/api/v1/trace/links/{link_id}/status", json={"status": "verified"}
    )
    assert status_response.status_code == 200

    # Reload the trace state as if the frontend navigated away and back,
    # without re-running extraction or matching.
    reload_response = client.get(f"/api/v1/trace/{doc_id}")
    assert reload_response.status_code == 200
    reload_data = reload_response.json()

    assert reload_data["total_claims"] == 1
    assert len(reload_data["claims"]) == 1
    assert reload_data["claims"][0]["id"] == claim_id

    reloaded_link = next(link for link in reload_data["links"] if link["id"] == link_id)
    assert reloaded_link["status"] == "verified"


def test_compliance_reflects_requirement_coverage_after_trace():
    doc_id = _create_document()

    claim_a_id = f"claim-a-{uuid.uuid4()}"
    claim_b_id = f"claim-b-{uuid.uuid4()}"
    seeded_claims = [
        ExtractedClaim(
            id=claim_a_id,
            document_id=doc_id,
            statement="Hash the password securely.",
            section=None,
        ),
        ExtractedClaim(
            id=claim_b_id,
            document_id=doc_id,
            statement="Send a welcome email on signup.",
            section=None,
        ),
    ]
    claim_repository.save_claims_for_document(doc_id, seeded_claims)

    trace_response = client.post(
        "/api/v1/trace/",
        json={
            "document_id": doc_id,
            "files": [
                {
                    "filepath": "auth.py",
                    "source_code": (
                        "def hash_password(password):\n"
                        "    '''Hash password securely.'''\n"
                        "    pass\n"
                    ),
                }
            ],
        },
    )
    assert trace_response.status_code == 200
    links = trace_response.json()["links"]
    link_for_claim_a = next(link for link in links if link["claim_id"] == claim_a_id)

    client.patch(
        f"/api/v1/trace/links/{link_for_claim_a['id']}/status",
        json={"status": "verified"},
    )

    compliance_response = client.get(f"/api/v1/compliance/{doc_id}")
    assert compliance_response.status_code == 200
    compliance = compliance_response.json()

    # 2 requirements total: one verified+traced, one entirely untraced
    # (no code matches "welcome email").
    assert compliance["total_claims"] == 2
    assert compliance["verified_claims"] == 1
    assert compliance["untraced_claims"] == 1
    assert compliance["compliance_percentage"] == 50.0
