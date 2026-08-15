from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.compliance_service import compliance_service

router = APIRouter()


class ComplianceResponse(BaseModel):
    document_id: str
    document_title: str
    total_claims: int
    traced_claims: int
    untraced_claims: int
    verified_claims: int
    rejected_claims: int
    pending_claims: int
    total_links: int
    strong_matches: int
    weak_matches: int
    compliance_percentage: float
    coverage_percentage: float


@router.get("/{document_id}", response_model=ComplianceResponse, tags=["Compliance"])
async def get_compliance_metrics(document_id: str) -> ComplianceResponse:
    metrics = compliance_service.get_document_compliance(document_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Document not found")
    return ComplianceResponse(**metrics)
