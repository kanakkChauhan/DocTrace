from collections import defaultdict

from backend.infrastructure.claim_repository import claim_repository
from backend.infrastructure.repository import document_repository
from backend.infrastructure.trace_repository import trace_repository


class ComplianceService:
    def get_document_compliance(self, document_id: str) -> dict | None:
        doc = document_repository.get_by_id(document_id)
        if not doc:
            return None

        claims = claim_repository.get_claims_for_document(document_id)
        links = trace_repository.get_links_for_document(document_id)

        total_claims = len(claims)
        total_links = len(links)
        strong_matches = sum(1 for _, l in links if l.match_type == "strong")
        weak_matches = sum(1 for _, l in links if l.match_type == "weak")

        links_by_claim: dict[str, list] = defaultdict(list)
        for _, link in links:
            links_by_claim[link.claim_id].append(link)

        verified_claims = 0
        rejected_claims = 0
        pending_claims = 0
        untraced_claims = 0

        for claim in claims:
            claim_links = links_by_claim.get(claim.id, [])
            if not claim_links:
                untraced_claims += 1
            elif any(l.status == "verified" for l in claim_links):
                verified_claims += 1
            elif all(l.status == "rejected" for l in claim_links):
                rejected_claims += 1
            else:
                pending_claims += 1

        traced_claims = total_claims - untraced_claims

        # Compliance measures verified coverage of actual requirements, not
        # raw link counts, so it can't be inflated by many weak links against
        # a small handful of claims.
        compliance_percentage = (
            round((verified_claims / total_claims) * 100, 1) if total_claims else 0.0
        )
        coverage_percentage = (
            round((traced_claims / total_claims) * 100, 1) if total_claims else 0.0
        )

        return {
            "document_id": document_id,
            "document_title": doc.title,
            "total_claims": total_claims,
            "traced_claims": traced_claims,
            "untraced_claims": untraced_claims,
            "verified_claims": verified_claims,
            "rejected_claims": rejected_claims,
            "pending_claims": pending_claims,
            "total_links": total_links,
            "strong_matches": strong_matches,
            "weak_matches": weak_matches,
            "compliance_percentage": compliance_percentage,
            "coverage_percentage": coverage_percentage,
        }


compliance_service = ComplianceService()
