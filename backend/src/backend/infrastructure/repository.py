from src.backend.domain.models import Document


class DocumentRepository:
    # Simple in memory dict storage for now, will hook up SQLite/Postgres later

    def __init__(self) -> None:
        self._storage: dict[str, Document] = {}

    def save(self, document: Document) -> Document:
        self._storage[document.id] = document
        return document

    def get_by_id(self, document_id: str) -> Document | None:
        return self._storage.get(document_id)

    def list_all(self) -> list[Document]:
        return list(self._storage.values())


# Singleton instance used across dependency injection boundaries
document_repository = DocumentRepository()
