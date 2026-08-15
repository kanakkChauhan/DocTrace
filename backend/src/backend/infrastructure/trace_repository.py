from sqlalchemy.orm import Session

from backend.domain.trace_models import TraceLink
from backend.infrastructure.database import Base, SessionLocal, engine
from backend.infrastructure.orm_models import TraceLinkORM

Base.metadata.create_all(bind=engine)


class TraceRepository:
    def __init__(self, db_session_factory=SessionLocal) -> None:
        self.Session = db_session_factory

    def save_links_for_document(self, document_id: str, links: list[TraceLink]) -> None:
        db: Session = self.Session()
        try:
            # Clear previous links for this document on re-trace
            db.query(TraceLinkORM).filter(
                TraceLinkORM.document_id == document_id
            ).delete()
            for link in links:
                orm_link = TraceLinkORM.from_domain(link, document_id)
                db.add(orm_link)
            db.commit()
        finally:
            db.close()

    def get_links_for_document(self, document_id: str) -> list[tuple[str, TraceLink]]:
        db: Session = self.Session()
        try:
            orm_links = (
                db.query(TraceLinkORM)
                .filter(TraceLinkORM.document_id == document_id)
                .all()
            )
            return [(l.id, l.to_domain()) for l in orm_links]
        finally:
            db.close()

    def update_link_status(self, link_id: str, status: str) -> bool:
        db: Session = self.Session()
        try:
            orm_link = db.query(TraceLinkORM).filter(TraceLinkORM.id == link_id).first()
            if not orm_link:
                return False
            orm_link.status = status
            db.commit()
            return True
        finally:
            db.close()


trace_repository = TraceRepository()
