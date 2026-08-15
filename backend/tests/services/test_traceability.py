from backend.domain.ast_models import (
    CodeLocation,
    ParsedClass,
    ParsedFunction,
    ParsedModule,
)
from backend.domain.models import ExtractedClaim
from backend.services.traceability import TraceabilityService


def test_evaluate_empty_claim():
    svc = TraceabilityService()
    claim = ExtractedClaim(id="1", document_id="doc1", statement="")
    assert not svc.evaluate_claim(claim, [])


def test_evaluate_no_match():
    svc = TraceabilityService()
    claim = ExtractedClaim(id="1", document_id="doc1", statement="Process payments")
    mod = ParsedModule(name="auth", filepath="auth.py")
    assert not svc.evaluate_claim(claim, [mod])


def test_evaluate_function_match():
    svc = TraceabilityService()
    claim = ExtractedClaim(
        id="1", document_id="doc1", statement="Hash the password securely."
    )
    func = ParsedFunction(
        name="hash_password",
        location=CodeLocation(1),
        is_method=False,
        docstring="Hash password securely.",
    )
    mod = ParsedModule(name="auth", filepath="auth.py", functions=[func])
    links = svc.evaluate_claim(claim, [mod])
    assert len(links) == 1
    assert links[0].match_type == "strong"


def test_parent_class_context_boost_and_inheritance():
    svc = TraceabilityService()
    # 3 meaningful keywords: "save", "user", "data"
    claim = ExtractedClaim(id="1", document_id="doc1", statement="Save the user data.")

    method = ParsedFunction(
        name="save",
        location=CodeLocation(line=5),
        is_method=True,
        docstring="Save data.",
    )

    cls = ParsedClass(
        name="UserDataStore",
        location=CodeLocation(line=1),
        bases=["BaseDataSaver"],
        methods=[method],
    )
    mod = ParsedModule(name="db", filepath="db.py", classes=[cls])

    links = svc.evaluate_claim(claim, [mod])

    assert len(links) == 2

    class_link = next(l for l in links if l.code_element_type == "class")
    method_link = next(l for l in links if l.code_element_type == "method")

    # UPDATE: The improved algorithm now scores this high enough to be "strong"
    assert class_link.match_type == "strong"
    assert method_link.match_type == "strong"


def test_evaluate_module_match():
    svc = TraceabilityService()
    claim = ExtractedClaim(
        id="1", document_id="doc1", statement="Authentication module"
    )
    mod = ParsedModule(
        name="auth", filepath="auth.py", docstring="Authentication module"
    )
    links = svc.evaluate_claim(claim, [mod])
    assert len(links) == 1


def test_evaluate_all():
    svc = TraceabilityService()
    claim = ExtractedClaim(id="1", document_id="doc1", statement="Test claim")
    links = svc.evaluate_all([claim], [])
    assert len(links) == 0
