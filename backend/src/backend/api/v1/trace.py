from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from backend.api.v1.documents import ClaimResponse
from backend.domain.ast_models import CodeLocation
from backend.infrastructure.ast_parser import analyze_source_code
from backend.infrastructure.claim_repository import claim_repository
from backend.infrastructure.repository import document_repository
from backend.infrastructure.trace_repository import trace_repository
from backend.services.extractor import ClaimExtractionError, claim_extractor
from backend.services.github_service import github_service
from backend.services.orchestrator import TraceabilityOrchestrator
from backend.services.traceability import TraceabilityService

router = APIRouter()


def get_orchestrator() -> TraceabilityOrchestrator:
    return TraceabilityOrchestrator(
        ast_parser=analyze_source_code,
        traceability_service=TraceabilityService(),
    )


class SourceFilePayload(BaseModel):
    filepath: str = Field(..., min_length=1)
    source_code: str = Field(..., min_length=1)


class TraceRequest(BaseModel):
    document_id: str
    files: list[SourceFilePayload] | None = None
    github_url: str | None = None


class TraceLinkResponse(BaseModel):
    id: str | None = None
    claim_id: str
    code_element_type: str
    code_element_name: str
    filepath: str
    location: CodeLocation
    match_type: str
    match_score: float
    evidence: list[str]
    status: str


class TraceStateResponse(BaseModel):
    document_id: str
    total_claims: int
    total_matches: int
    claims: list[ClaimResponse]
    links: list[TraceLinkResponse]


class StatusUpdatePayload(BaseModel):
    status: str = Field(..., pattern="^(pending|verified|rejected)$")


def _build_response(document_id: str) -> TraceStateResponse:
    """Assembles the current persisted claim + trace-link state for a document."""
    claims = claim_repository.get_claims_for_document(document_id)
    persisted_links = trace_repository.get_links_for_document(document_id)

    response_links = [
        TraceLinkResponse(
            id=link_id,
            claim_id=link.claim_id,
            code_element_type=link.code_element_type,
            code_element_name=link.code_element_name,
            filepath=link.filepath,
            location=link.location,
            match_type=link.match_type,
            match_score=link.match_score,
            evidence=link.evidence,
            status=link.status,
        )
        for link_id, link in persisted_links
    ]

    return TraceStateResponse(
        document_id=document_id,
        total_claims=len(claims),
        total_matches=len(response_links),
        claims=[ClaimResponse.from_domain(c) for c in claims],
        links=response_links,
    )


@router.post("/", response_model=TraceStateResponse, tags=["Traceability"])
async def run_traceability(
    payload: TraceRequest,
    orchestrator: TraceabilityOrchestrator = Depends(get_orchestrator),
) -> TraceStateResponse:
    document = document_repository.get_by_id(payload.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Claims must have stable ids across requests. Use whatever was persisted
    # by the most recent /extract call; only extract here as a fallback, so
    # the pipeline is still runnable in one shot if a caller skips the
    # explicit extract step.
    claims = claim_repository.get_claims_for_document(document.id)
    if not claims:
        try:
            claims = await claim_extractor.extract_claims(document)
        except ClaimExtractionError as e:
            raise HTTPException(status_code=503, detail=str(e)) from e
        claim_repository.save_claims_for_document(document.id, claims)

    code_files: list[tuple[str, str]] = []

    if payload.github_url:
        try:
            # fetch_repository_files does blocking network I/O (requests).
            # Running it directly here would block the whole event loop for
            # every other in-flight request, so it's offloaded to a worker
            # thread instead.
            code_files = await run_in_threadpool(
                github_service.fetch_repository_files, payload.github_url
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    elif payload.files is not None:
        code_files = [(f.filepath, f.source_code) for f in payload.files]

    links = orchestrator.run_trace(claims, code_files)

    trace_repository.save_links_for_document(document.id, links)

    return _build_response(document.id)


@router.get("/{document_id}", response_model=TraceStateResponse, tags=["Traceability"])
async def get_trace_state(document_id: str) -> TraceStateResponse:
    """
    Reads back whatever claims and trace links already exist for a document,
    without re-running extraction or matching. This is what the frontend uses
    to reload a previously traced document instead of re-extracting claims
    (which would mint new, unrelated claim ids on every reload).
    """
    document = document_repository.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return _build_response(document_id)


@router.patch("/links/{link_id}/status", status_code=200, tags=["Traceability"])
async def update_link_status(link_id: str, payload: StatusUpdatePayload) -> dict:
    success = trace_repository.update_link_status(link_id, payload.status)
    if not success:
        raise HTTPException(status_code=404, detail="Trace link not found")
    return {"status": "success", "link_id": link_id, "new_status": payload.status}
