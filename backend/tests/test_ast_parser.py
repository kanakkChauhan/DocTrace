from backend.infrastructure.ast_parser import analyze_source_code

SAMPLE_CODE = """
import os
from typing import List

@app.get("/items")
async def fetch_items(limit: int = 10) -> List[str]:
    '''Fetches items from the database.'''
    return ["item1", "item2"]

class DocumentHandler:
    '''Handles document operations.'''
    
    def process(self, doc_id: str):
        pass
"""


def test_ast_analyzer_module_and_imports():
    module = analyze_source_code(
        SAMPLE_CODE, filepath="sample.py", module_name="sample"
    )
    assert module.name == "sample"
    assert "os" in module.imports
    assert "typing.List" in module.imports


def test_ast_analyzer_functions():
    module = analyze_source_code(
        SAMPLE_CODE, filepath="sample.py", module_name="sample"
    )
    assert len(module.functions) == 1
    func = module.functions[0]

    assert func.name == "fetch_items"
    assert func.is_async is True
    assert func.is_route is True
    assert func.docstring == "Fetches items from the database."
    assert func.return_annotation == "List[str]"
    assert func.args[0].name == "limit"
    assert func.args[0].annotation == "int"


def test_ast_analyzer_classes():
    module = analyze_source_code(
        SAMPLE_CODE, filepath="sample.py", module_name="sample"
    )
    assert len(module.classes) == 1
    cls = module.classes[0]

    assert cls.name == "DocumentHandler"
    assert cls.docstring == "Handles document operations."

    method = cls.methods[0]
    assert method.name == "process"
    assert method.is_method is True
    assert method.args[1].name == "doc_id"
    assert method.args[1].annotation == "str"
