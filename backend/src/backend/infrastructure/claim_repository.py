from sqlalchemy.orm import Session

from backend.domain.models import ExtractedClaim
from backend.infrastructure.database import Base, SessionLocal, engine
from backend.infrastructure.orm_models import ClaimORM

Base.metadata.create_all(bind=engine)


class ClaimRepository:
    def __init__(self, db_session_factory=SessionLocal) -> None:
        self.Session = db_session_factory

    def save_claims_for_document(
        self, document_id: str, claims: list[ExtractedClaim]
    ) -> None:
        db: Session = self.Session()
        try:
            # Clear previous claims for this document on re-extraction, so claim
            # identity always matches the most recently persisted extraction run.
            db.query(ClaimORM).filter(ClaimORM.document_id == document_id).delete()
            for claim in claims:
                db.add(ClaimORM.from_domain(claim))
            db.commit()
        finally:
            db.close()

    def get_claims_for_document(self, document_id: str) -> list[ExtractedClaim]:
        db: Session = self.Session()
        try:
            orm_claims = (
                db.query(ClaimORM).filter(ClaimORM.document_id == document_id).all()
            )
            return [c.to_domain() for c in orm_claims]
        finally:
            db.close()

    def get_by_id(self, claim_id: str) -> ExtractedClaim | None:
        db: Session = self.Session()
        try:
            orm_claim = db.query(ClaimORM).filter(ClaimORM.id == claim_id).first()
            return orm_claim.to_domain() if orm_claim else None
        finally:
            db.close()


claim_repository = ClaimRepository()
