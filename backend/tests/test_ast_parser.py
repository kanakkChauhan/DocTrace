import textwrap

from backend.infrastructure.ast_parser import analyze_source_code


def test_ast_analyzer_module_and_imports() -> None:
    source = textwrap.dedent('''\
    """Module docstring for testing traceability."""
    import os
    from fastapi import APIRouter
    ''')
    parsed = analyze_source_code(source, "test_mod.py", "test_mod")
    assert parsed.name == "test_mod"
    assert parsed.docstring == "Module docstring for testing traceability."
    assert "os" in parsed.imports
    assert "fastapi.APIRouter" in parsed.imports


def test_ast_analyzer_functions() -> None:
    source = textwrap.dedent('''\
    async def sample_endpoint(user_id: str) -> dict:
        """Fetch user details."""
        return {"id": user_id}
    ''')
    parsed = analyze_source_code(source, "test_func.py", "test_func")
    assert len(parsed.functions) == 1
    func = parsed.functions[0]
    assert func.name == "sample_endpoint"
    assert func.is_async is True
    assert func.docstring == "Fetch user details."
    assert func.return_annotation == "dict"
    assert len(func.args) == 1
    assert func.args[0].name == "user_id"
    assert func.args[0].annotation == "str"


def test_ast_analyzer_classes_and_bases() -> None:
    source = textwrap.dedent('''\
    class BaseRepository:
        """Base repository class."""
        pass

    class UserRepository(BaseRepository):
        """User repository implementation."""
        def get_user(self, user_id: str) -> None:
            pass
    ''')
    parsed = analyze_source_code(source, "test_class.py", "test_class")
    assert len(parsed.classes) == 2

    base_class = parsed.classes[0]
    assert base_class.name == "BaseRepository"
    assert base_class.docstring == "Base repository class."
    assert base_class.bases == []

    user_class = parsed.classes[1]
    assert user_class.name == "UserRepository"
    assert user_class.docstring == "User repository implementation."
    assert user_class.bases == ["BaseRepository"]
    assert len(user_class.methods) == 1
    assert user_class.methods[0].name == "get_user"
    assert user_class.methods[0].is_method is True
