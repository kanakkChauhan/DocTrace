import hashlib
import json

import openai
from openai import AsyncOpenAI
from pydantic import BaseModel, ValidationError

from backend.core.config import settings
from backend.domain.models import Document, ExtractedClaim


class ClaimExtractionError(Exception):
    """
    Raised whenever claim extraction cannot legitimately be completed:
    missing configuration, a provider/network failure, or output that
    doesn't match the expected schema. Callers must surface this as a real
    error to the caller/user -- it must never be swallowed to fabricate
    claims.
    """


class LLMClaim(BaseModel):
    statement: str
    section: str | None = None


class ClaimExtractionService:
    # Service to parse documents and extract testable claims using Groq.

    async def extract_claims(self, document: Document) -> list[ExtractedClaim]:
        if not settings.GROQ_API_KEY:
            raise ClaimExtractionError(
                "Claim extraction is not configured: GROQ_API_KEY is missing."
            )

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

        try:
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
        except openai.RateLimitError as e:
            raise ClaimExtractionError(
                "The claim extraction provider is rate-limited. Please try again shortly."
            ) from e
        except openai.AuthenticationError as e:
            raise ClaimExtractionError(
                "The claim extraction provider rejected the configured API key."
            ) from e
        except openai.APIConnectionError as e:
            raise ClaimExtractionError(
                "Could not reach the claim extraction provider (network error)."
            ) from e
        except openai.APIError as e:
            raise ClaimExtractionError(
                f"The claim extraction provider returned an error: {e}"
            ) from e

        raw_content = response.choices[0].message.content or "{}"
        try:
            data = json.loads(raw_content)
        except json.JSONDecodeError as e:
            raise ClaimExtractionError(
                "The claim extraction provider returned malformed (non-JSON) output."
            ) from e

        if not isinstance(data, dict):
            raise ClaimExtractionError(
                "The claim extraction provider returned an unexpected response shape."
            )

        raw_claims = data.get("claims", [])
        if not isinstance(raw_claims, list):
            raise ClaimExtractionError(
                "The claim extraction provider returned an unexpected response shape."
            )

        claims: list[ExtractedClaim] = []
        for raw_claim in raw_claims:
            if not isinstance(raw_claim, dict):
                continue
            try:
                llm_claim = LLMClaim(**raw_claim)
            except ValidationError:
                # Skip individual malformed entries rather than failing the
                # whole extraction over one bad item from the provider.
                continue
            if not llm_claim.statement:
                continue

            # Deterministic ID based on document context and statement
            deterministic_id = hashlib.md5(
                f"{document.id}_{llm_claim.statement}".encode("utf-8")
            ).hexdigest()

            claims.append(
                ExtractedClaim(
                    id=deterministic_id,
                    document_id=document.id,
                    statement=llm_claim.statement,
                    section=llm_claim.section,
                )
            )

        return claims


# Singleton instance for dependency injection
claim_extractor = ClaimExtractionService()
