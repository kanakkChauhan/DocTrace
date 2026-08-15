from backend.domain.ast_models import ParsedModule
from backend.domain.models import ExtractedClaim
from backend.services.orchestrator import TraceabilityOrchestrator
from backend.services.traceability import TraceabilityService


def _fake_ast_parser(source_code: str, filepath: str, module_name: str) -> ParsedModule:
    return ParsedModule(
        name=module_name, filepath=filepath, docstring="Authentication module"
    )


def test_run_trace_with_no_claims_returns_empty():
    orchestrator = TraceabilityOrchestrator(
        ast_parser=_fake_ast_parser, traceability_service=TraceabilityService()
    )
    links = orchestrator.run_trace([], [("auth.py", "x = 1")])
    assert links == []


def test_run_trace_with_no_files_returns_empty():
    orchestrator = TraceabilityOrchestrator(
        ast_parser=_fake_ast_parser, traceability_service=TraceabilityService()
    )
    claim = ExtractedClaim(
        id="c1", document_id="doc-1", statement="Authentication module"
    )
    links = orchestrator.run_trace([claim], [])
    assert links == []


def test_run_trace_skips_files_with_syntax_errors():
    def broken_parser(source_code, filepath, module_name):
        raise SyntaxError("bad syntax")

    orchestrator = TraceabilityOrchestrator(
        ast_parser=broken_parser, traceability_service=TraceabilityService()
    )
    claim = ExtractedClaim(
        id="c1", document_id="doc-1", statement="Authentication module"
    )
    links = orchestrator.run_trace([claim], [("broken.py", "not valid python (")])
    assert links == []


def test_run_trace_matches_claim_against_module_docstring():
    orchestrator = TraceabilityOrchestrator(
        ast_parser=_fake_ast_parser, traceability_service=TraceabilityService()
    )
    claim = ExtractedClaim(
        id="c1", document_id="doc-1", statement="Authentication module"
    )
    links = orchestrator.run_trace(
        [claim], [("auth.py", "# real source unused by fake parser")]
    )
    assert len(links) == 1
    assert links[0].claim_id == "c1"
    assert links[0].code_element_type == "module"
