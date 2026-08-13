from fastapi.testclient import TestClient

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
