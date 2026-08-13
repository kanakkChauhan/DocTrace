from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.backend.domain.models import Document
from src.backend.infrastructure.repository import document_repository

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
