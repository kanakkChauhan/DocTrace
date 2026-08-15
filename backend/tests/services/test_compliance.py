from unittest.mock import patch

from backend.domain.ast_models import CodeLocation
from backend.domain.models import Document, ExtractedClaim
from backend.domain.trace_models import TraceLink
from backend.services.compliance_service import ComplianceService


@patch("backend.services.compliance_service.claim_repository.get_claims_for_document")
@patch("backend.services.compliance_service.document_repository.get_by_id")
@patch("backend.services.compliance_service.trace_repository.get_links_for_document")
def test_compliance_calculation(mock_get_links, mock_get_doc, mock_get_claims):
    mock_get_doc.return_value = Document(
        id="doc-1", title="Test Spec", content="Content"
    )
    mock_get_claims.return_value = [
        ExtractedClaim(
            id="c1", document_id="doc-1", statement="Hash passwords.", section=None
        ),
        ExtractedClaim(
            id="c2", document_id="doc-1", statement="Expire tokens.", section=None
        ),
        ExtractedClaim(
            id="c3", document_id="doc-1", statement="Log audit events.", section=None
        ),
    ]
    mock_get_links.return_value = [
        (
            "l1",
            TraceLink(
                claim_id="c1",
                code_element_type="function",
                code_element_name="foo",
                filepath="a.py",
                location=CodeLocation(line=1),
                match_type="strong",
                match_score=0.9,
                status="verified",
            ),
        ),
        (
            "l2",
            TraceLink(
                claim_id="c2",
                code_element_type="function",
                code_element_name="bar",
                filepath="b.py",
                location=CodeLocation(line=5),
                match_type="weak",
                match_score=0.5,
                status="pending",
            ),
        ),
        # c3 has no links at all -> untraced
    ]

    service = ComplianceService()
    metrics = service.get_document_compliance("doc-1")

    assert metrics["total_claims"] == 3
    assert metrics["traced_claims"] == 2
    assert metrics["untraced_claims"] == 1
    assert metrics["verified_claims"] == 1
    assert metrics["pending_claims"] == 1
    assert metrics["rejected_claims"] == 0
    assert metrics["total_links"] == 2
    assert metrics["strong_matches"] == 1
    assert metrics["weak_matches"] == 1
    assert metrics["compliance_percentage"] == round((1 / 3) * 100, 1)
    assert metrics["coverage_percentage"] == round((2 / 3) * 100, 1)


@patch("backend.services.compliance_service.document_repository.get_by_id")
def test_compliance_returns_none_for_missing_document(mock_get_doc):
    mock_get_doc.return_value = None
    service = ComplianceService()
    assert service.get_document_compliance("missing") is None


@patch("backend.services.compliance_service.claim_repository.get_claims_for_document")
@patch("backend.services.compliance_service.document_repository.get_by_id")
@patch("backend.services.compliance_service.trace_repository.get_links_for_document")
def test_compliance_with_no_claims_is_zero_not_error(
    mock_get_links, mock_get_doc, mock_get_claims
):
    mock_get_doc.return_value = Document(
        id="doc-1", title="Empty Spec", content="Content"
    )
    mock_get_claims.return_value = []
    mock_get_links.return_value = []

    service = ComplianceService()
    metrics = service.get_document_compliance("doc-1")

    assert metrics["total_claims"] == 0
    assert metrics["compliance_percentage"] == 0.0
    assert metrics["coverage_percentage"] == 0.0
