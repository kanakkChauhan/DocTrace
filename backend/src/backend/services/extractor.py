import asyncio
from uuid import uuid4

from src.backend.domain.models import Document, ExtractedClaim


class ClaimExtractionService:
    # Service to handle parsing documents and extracting testable claims.
    # Currently using a simulated delay/response to establish the architecture.

    async def extract_claims(self, document: Document) -> list[ExtractedClaim]:
        # Simulate network call to an LLM
        await asyncio.sleep(1.0)

        # Simulated extraction logic based on document content
        claims = [
            ExtractedClaim(
                id=str(uuid4()),
                document_id=document.id,
                statement="The system must support OAuth 2.0.",
                section="Authentication",
            ),
            ExtractedClaim(
                id=str(uuid4()),
                document_id=document.id,
                statement="Passwords must be at least 12 characters long.",
                section="Security",
            ),
        ]

        return claims

claim_extractor = ClaimExtractionService()
