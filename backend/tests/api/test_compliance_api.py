import pytest
from fastapi.testclient import TestClient

from backend.infrastructure.repository import document_repository
from main import app


@pytest.fixture
def client():
    document_repository._storage = (
        {} if hasattr(document_repository, "_storage") else None
    )
    return TestClient(app)


def test_compliance_endpoint_not_found(client):
    resp = client.get("/api/v1/compliance/non-existent")
    assert resp.status_code == 404
