from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Document:
    # Core doc entity for uploaded text specs
    id: str
    title: str
    content: str
    version: str = "v1.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ExtractedClaim:
    # Individual requirements pulled out of the document text
    id: str
    document_id: str
    statement: str
    section: str | None = None
