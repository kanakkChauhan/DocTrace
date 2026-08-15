from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.database import Base


class DocumentORM(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String, default="v1.0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    def to_domain(self):
        from backend.domain.models import Document

        return Document(
            id=self.id,
            title=self.title,
            content=self.content,
            version=self.version,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, doc):
        return cls(
            id=doc.id,
            title=doc.title,
            content=doc.content,
            version=doc.version,
            created_at=doc.created_at,
        )


class ClaimORM(Base):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    document_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    section: Mapped[str | None] = mapped_column(String, nullable=True)

    def to_domain(self):
        from backend.domain.models import ExtractedClaim

        return ExtractedClaim(
            id=self.id,
            document_id=self.document_id,
            statement=self.statement,
            section=self.section,
        )

    @classmethod
    def from_domain(cls, claim):
        return cls(
            id=claim.id,
            document_id=claim.document_id,
            statement=claim.statement,
            section=claim.section,
        )


class TraceLinkORM(Base):
    __tablename__ = "trace_links"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    claim_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    document_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    code_element_type: Mapped[str] = mapped_column(String, nullable=False)
    code_element_name: Mapped[str] = mapped_column(String, nullable=False)
    filepath: Mapped[str] = mapped_column(String, nullable=False)
    location_line: Mapped[float] = mapped_column(Float, nullable=False)
    location_end_line: Mapped[float | None] = mapped_column(Float, nullable=True)
    match_type: Mapped[str] = mapped_column(String, nullable=False)
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    evidence: Mapped[list[Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")

    def to_domain(self):
        from backend.domain.ast_models import CodeLocation
        from backend.domain.trace_models import TraceLink

        return TraceLink(
            claim_id=self.claim_id,
            code_element_type=self.code_element_type,
            code_element_name=self.code_element_name,
            filepath=self.filepath,
            location=CodeLocation(
                line=int(self.location_line),
                end_line=(
                    int(self.location_end_line)
                    if self.location_end_line is not None
                    else None
                ),
            ),
            match_type=self.match_type,
            match_score=self.match_score,
            evidence=self.evidence,
            status=self.status,
        )

    @classmethod
    def from_domain(cls, link, document_id: str):
        import uuid

        return cls(
            id=str(uuid.uuid4()),
            claim_id=link.claim_id,
            document_id=document_id,
            code_element_type=link.code_element_type,
            code_element_name=link.code_element_name,
            filepath=link.filepath,
            location_line=link.location.line,
            location_end_line=link.location.end_line,
            match_type=link.match_type,
            match_score=link.match_score,
            evidence=link.evidence,
            status=getattr(link, "status", "pending"),
        )
