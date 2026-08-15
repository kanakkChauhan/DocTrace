import re
import string

from backend.domain.ast_models import (
    CodeLocation,
    ParsedModule,
)
from backend.domain.models import ExtractedClaim
from backend.domain.trace_models import TraceLink

# Standard technical stopwords
STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "as",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "shall",
    "will",
    "should",
    "would",
    "may",
    "might",
    "must",
    "can",
    "could",
    "system",
    "it",
    "this",
    "that",
    "not",
    "if",
    "then",
}


def tokenize_text(text: str | None) -> set[str]:
    """Lowercases, strips punctuation, and removes stopwords and digits."""
    if not text:
        return set()
    text = text.translate(str.maketrans("", "", string.punctuation)).lower()
    # Filter out stopwords and standalone digits (like requirement list numbers)
    return {w for w in text.split() if w and w not in STOPWORDS and not w.isdigit()}


def tokenize_identifier(name: str) -> set[str]:
    """Splits snake_case and CamelCase identifiers into lowercase tokens."""
    name = name.replace("_", " ")
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    return tokenize_text(name.lower())


class TraceabilityService:
    def evaluate_claim(
        self, claim: ExtractedClaim, modules: list[ParsedModule]
    ) -> list[TraceLink]:
        """Evaluates a single claim against all parsed modules deterministically."""
        claim_kws = tokenize_text(claim.statement)
        if not claim_kws:
            return []  # Zero meaningful keywords

        links = []
        for mod in modules:
            links.extend(self._evaluate_module(claim, claim_kws, mod))

        # Deterministic ordering: Score descending, then alphabetical by element name
        links.sort(key=lambda x: (-x.match_score, x.code_element_name))
        return links

    def evaluate_all(
        self, claims: list[ExtractedClaim], modules: list[ParsedModule]
    ) -> list[TraceLink]:
        """Batch evaluates multiple claims."""
        all_links = []
        for claim in claims:
            all_links.extend(self.evaluate_claim(claim, modules))
        return all_links

    def _calc_base_score(
        self, claim_kws: set[str], name: str, docstring: str | None
    ) -> tuple[float, list[str]]:
        name_kws = tokenize_identifier(name)
        doc_kws = tokenize_text(docstring)

        # Flexible overlap: Match if one string is a substring of the other (handles plurals/tenses)
        name_overlap = {c for c in claim_kws if any(c in n or n in c for n in name_kws)}
        doc_overlap = {c for c in claim_kws if any(c in d or d in c for d in doc_kws)}

        # Score relative to identifier size/claim relevance to prevent overly harsh penalties for extra claim words
        name_score = len(name_overlap) / max(len(name_kws), 1) if name_kws else 0.0
        doc_score = len(doc_overlap) / max(len(doc_kws), 1) if doc_kws else 0.0

        if not doc_kws:
            base_score = name_score
        else:
            base_score = (0.6 * name_score) + (0.4 * doc_score)

        evidence = [
            f"Base score: {base_score:.2f} (Name overlap: {len(name_overlap)}/{len(name_kws) or 1}, Docstring overlap: {len(doc_overlap)}/{len(doc_kws) or 1})"
        ]
        return base_score, evidence

    def _create_link(
        self,
        claim_id: str,
        element_type: str,
        element_name: str,
        filepath: str,
        location: CodeLocation,
        final_score: float,
        evidence: list[str],
    ) -> TraceLink | None:
        final_score = min(final_score, 1.0)

        # Slightly more lenient thresholds to account for semantic phrasing gaps
        if final_score >= 0.6:
            match_type = "strong"
        elif final_score >= 0.2:
            match_type = "weak"
        else:
            return None  # Discard below 0.2

        return TraceLink(
            claim_id=claim_id,
            code_element_type=element_type,
            code_element_name=element_name,
            filepath=filepath,
            location=location,
            match_type=match_type,
            match_score=round(final_score, 4),
            evidence=evidence,
        )

    def _evaluate_module(
        self, claim: ExtractedClaim, claim_kws: set[str], mod: ParsedModule
    ) -> list[TraceLink]:
        links = []
        mod_fqn = mod.name

        # 1. Evaluate Module itself
        mod_base_score, mod_evidence = self._calc_base_score(
            claim_kws, mod.name, mod.docstring
        )
        link = self._create_link(
            claim.id,
            "module",
            mod_fqn,
            mod.filepath,
            CodeLocation(line=1),
            mod_base_score,
            mod_evidence,
        )
        if link:
            links.append(link)

        # 2. Evaluate Classes and their Methods
        for cls in mod.classes:
            cls_fqn = f"{mod_fqn}.{cls.name}"
            cls_base_score, cls_evidence = self._calc_base_score(
                claim_kws, cls.name, cls.docstring
            )
            cls_final_score = cls_base_score

            # Inheritance boost
            if cls.bases:
                base_kws = set()
                for base in cls.bases:
                    base_kws.update(tokenize_identifier(base))
                if any(c in b or b in c for c in claim_kws for b in base_kws):
                    cls_final_score += 0.1
                    cls_evidence.append("Inheritance boost: +0.10 (Base class overlap)")

            link = self._create_link(
                claim.id,
                "class",
                cls_fqn,
                mod.filepath,
                cls.location,
                cls_final_score,
                cls_evidence,
            )
            if link:
                links.append(link)

            # Evaluate Nested Methods
            for method in cls.methods:
                meth_fqn = f"{cls_fqn}.{method.name}"
                meth_base_score, meth_evidence = self._calc_base_score(
                    claim_kws, method.name, method.docstring
                )

                parent_boost = 0.2 * cls_base_score
                meth_final_score = meth_base_score + parent_boost
                if parent_boost > 0:
                    meth_evidence.append(
                        f"Parent context boost: +{parent_boost:.2f} (from {cls.name})"
                    )

                link = self._create_link(
                    claim.id,
                    "method",
                    meth_fqn,
                    mod.filepath,
                    method.location,
                    meth_final_score,
                    meth_evidence,
                )
                if link:
                    links.append(link)

        # 3. Evaluate Top-Level Functions
        for func in mod.functions:
            func_fqn = f"{mod_fqn}.{func.name}"
            func_base_score, func_evidence = self._calc_base_score(
                claim_kws, func.name, func.docstring
            )
            link = self._create_link(
                claim.id,
                "function",
                func_fqn,
                mod.filepath,
                func.location,
                func_base_score,
                func_evidence,
            )
            if link:
                links.append(link)

        return links
