import json
import uuid

from openai import AsyncOpenAI
from pydantic import BaseModel

from backend.core.config import settings
from backend.domain.models import Document, ExtractedClaim


class LLMClaim(BaseModel):
    statement: str
    section: str | None


class ClaimExtractionService:
    # Service to parse documents and extract testable claims using Groq.

    async def extract_claims(self, document: Document) -> list[ExtractedClaim]:
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not configured in the environment.")

        # Point OpenAI SDK to Groq's free endpoint
        client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY,
        )

        prompt = (
            f"Analyze the following technical specification and extract clear, testable requirements.\n"
            f"Return ONLY valid JSON matching this exact structure: "
            f'{{"claims": [{{"statement": "...", "section": "..."}}]}}\n\n'
            f"Document Title: {document.title}\n\n"
            f"Content:\n{document.content}"
        )

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a technical requirements extractor. Return JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        raw_content = response.choices[0].message.content or "{}"
        data = json.loads(raw_content)
        raw_claims = data.get("claims", [])

        claims = [
            ExtractedClaim(
                id=str(uuid.uuid4()),
                document_id=document.id,
                statement=c.get("statement", ""),
                section=c.get("section"),
            )
            for c in raw_claims
            if c.get("statement")
        ]

        return claims


# Singleton instance for dependency injection
claim_extractor = ClaimExtractionService()
