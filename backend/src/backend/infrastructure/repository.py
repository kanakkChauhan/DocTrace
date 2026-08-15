from sqlalchemy.orm import Session

from backend.domain.models import Document
from backend.infrastructure.database import Base, SessionLocal, engine
from backend.infrastructure.orm_models import DocumentORM

# Ensure tables are created
Base.metadata.create_all(bind=engine)


class DocumentRepository:
    def __init__(self, db_session_factory=SessionLocal) -> None:
        self.Session = db_session_factory

    def save(self, document: Document) -> Document:
        db: Session = self.Session()
        try:
            existing = (
                db.query(DocumentORM).filter(DocumentORM.id == document.id).first()
            )
            if existing:
                existing.title = document.title
                existing.content = document.content
                existing.version = document.version
            else:
                orm_doc = DocumentORM.from_domain(document)
                db.add(orm_doc)
            db.commit()
            return document
        finally:
            db.close()

    def get_by_id(self, document_id: str) -> Document | None:
        db: Session = self.Session()
        try:
            orm_doc = (
                db.query(DocumentORM).filter(DocumentORM.id == document_id).first()
            )
            return orm_doc.to_domain() if orm_doc else None
        finally:
            db.close()

    def list_all(self) -> list[Document]:
        db: Session = self.Session()
        try:
            orm_docs = db.query(DocumentORM).all()
            return [d.to_domain() for d in orm_docs]
        finally:
            db.close()

    def delete(self, document_id: str) -> bool:
        db: Session = self.Session()
        try:
            orm_doc = (
                db.query(DocumentORM).filter(DocumentORM.id == document_id).first()
            )
            if not orm_doc:
                return False
            db.delete(orm_doc)
            db.commit()
            return True
        finally:
            db.close()


document_repository = DocumentRepository()
