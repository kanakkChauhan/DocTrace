from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.domain.models import Document, ExtractedClaim
from backend.infrastructure.claim_repository import claim_repository
from backend.infrastructure.repository import document_repository
from backend.services.extractor import ClaimExtractionError, claim_extractor

router = APIRouter()


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    version: str = Field(default="v1.0")


class DocumentResponse(BaseModel):
    id: str
    title: str
    content: str
    version: str
    created_at: datetime

    @classmethod
    def from_domain(cls, doc: Document) -> "DocumentResponse":
        return cls(
            id=doc.id,
            title=doc.title,
            content=doc.content,
            version=doc.version,
            created_at=doc.created_at,
        )


@router.post("/", response_model=DocumentResponse, status_code=201, tags=["Documents"])
async def create_document(payload: DocumentCreate) -> DocumentResponse:
    doc_id = str(uuid4())
    document = Document(
        id=doc_id,
        title=payload.title,
        content=payload.content,
        version=payload.version,
    )
    saved = document_repository.save(document)
    return DocumentResponse.from_domain(saved)


@router.get("/", response_model=list[DocumentResponse], tags=["Documents"])
async def list_documents() -> list[DocumentResponse]:
    docs = document_repository.list_all()
    return [DocumentResponse.from_domain(d) for d in docs]


@router.get("/{document_id}", response_model=DocumentResponse, tags=["Documents"])
async def get_document(document_id: str) -> DocumentResponse:
    doc = document_repository.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.from_domain(doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str) -> None:
    deleted = document_repository.delete(document_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")


class ClaimResponse(BaseModel):
    id: str
    document_id: str
    statement: str
    section: str | None

    @classmethod
    def from_domain(cls, claim: ExtractedClaim) -> "ClaimResponse":
        return cls(
            id=claim.id,
            document_id=claim.document_id,
            statement=claim.statement,
            section=claim.section,
        )


@router.post(
    "/{document_id}/extract", response_model=list[ClaimResponse], tags=["Extraction"]
)
async def extract_document_claims(document_id: str) -> list[ClaimResponse]:
    """
    Runs claim extraction and persists the result as the document's current
    set of requirements, replacing any claims from a previous extraction.
    Downstream trace runs and reloads read from this persisted set, so claim
    identity stays stable across requests instead of a fresh uuid being
    minted on every call.
    """
    doc = document_repository.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        claims = await claim_extractor.extract_claims(doc)
    except ClaimExtractionError as e:
        # Missing config, provider failure, or malformed provider output --
        # never fabricate claims here, just surface a clean, honest error.
        raise HTTPException(status_code=503, detail=str(e)) from e

    claim_repository.save_claims_for_document(document_id, claims)
    return [ClaimResponse.from_domain(c) for c in claims]
