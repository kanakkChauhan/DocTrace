import ast

from backend.domain.ast_models import (
    CodeLocation,
    ParsedArgument,
    ParsedClass,
    ParsedFunction,
    ParsedModule,
)


class DocTraceASTVisitor(ast.NodeVisitor):
    """Visits AST nodes to extract structured code information."""

    def __init__(self, filepath: str, module_name: str) -> None:
        self.module = ParsedModule(name=module_name, filepath=filepath)
        self.current_class: ParsedClass | None = None

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.module.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module_name = node.module or ""
        for alias in node.names:
            self.module.imports.append(f"{module_name}.{alias.name}")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        docstring = ast.get_docstring(node)
        parsed_class = ParsedClass(
            name=node.name,
            location=CodeLocation(line=node.lineno, end_line=node.end_lineno),
            docstring=docstring,
        )
        self.module.classes.append(parsed_class)

        previous_class = self.current_class
        self.current_class = parsed_class
        self.generic_visit(node)
        self.current_class = previous_class

    def _extract_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool
    ) -> None:
        docstring = ast.get_docstring(node)

        args = []
        for arg in node.args.args:
            annotation = ast.unparse(arg.annotation) if arg.annotation else None
            args.append(ParsedArgument(name=arg.arg, annotation=annotation))

        decorators = [ast.unparse(dec) for dec in node.decorator_list]
        is_route = any(
            "get" in dec or "post" in dec or "router" in dec for dec in decorators
        )

        return_annotation = ast.unparse(node.returns) if node.returns else None

        parsed_func = ParsedFunction(
            name=node.name,
            location=CodeLocation(line=node.lineno, end_line=node.end_lineno),
            args=args,
            return_annotation=return_annotation,
            decorators=decorators,
            docstring=docstring,
            is_method=self.current_class is not None,
            is_async=is_async,
            is_route=is_route,
        )

        if self.current_class:
            self.current_class.methods.append(parsed_func)
        else:
            self.module.functions.append(parsed_func)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._extract_function(node, is_async=False)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._extract_function(node, is_async=True)
        self.generic_visit(node)


def analyze_source_code(
    source_code: str, filepath: str, module_name: str
) -> ParsedModule:
    """Parses raw Python source code and returns a structured ParsedModule."""
    tree = ast.parse(source_code, filename=filepath)
    visitor = DocTraceASTVisitor(filepath=filepath, module_name=module_name)
    visitor.visit(tree)
    return visitor.module
