import logging
from typing import Protocol

from backend.domain.ast_models import ParsedModule
from backend.domain.models import ExtractedClaim
from backend.domain.trace_models import TraceLink
from backend.services.traceability import TraceabilityService

logger = logging.getLogger(__name__)


class ASTParserCallable(Protocol):
    def __call__(
        self, source_code: str, filepath: str, module_name: str
    ) -> ParsedModule: ...


class TraceabilityOrchestrator:
    """
    Runs AST parsing and deterministic trace matching against an already
    resolved set of claims. Claim extraction is intentionally NOT owned by
    this class: claims are persisted independently (see claim_repository) so
    that a claim's id stays stable whether it's reached via a fresh trace run
    or a reload of previously computed results.
    """

    def __init__(
        self,
        ast_parser: ASTParserCallable,
        traceability_service: TraceabilityService,
    ) -> None:
        self.ast_parser = ast_parser
        self.traceability_service = traceability_service

    def run_trace(
        self, claims: list[ExtractedClaim], files: list[tuple[str, str]]
    ) -> list[TraceLink]:
        """
        Evaluates a fixed set of claims against a set of source files.
        """
        if not claims:
            return []

        modules = []
        for filepath, source_code in files:
            module_name = filepath.replace("/", ".").replace(".py", "")
            try:
                parsed_module = self.ast_parser(source_code, filepath, module_name)
                modules.append(parsed_module)
            except (SyntaxError, IndentationError) as e:
                logger.warning(
                    "Syntax error parsing %s: %s. Skipping file.", filepath, e
                )

        if not modules:
            return []

        return self.traceability_service.evaluate_all(claims, modules)
