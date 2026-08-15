from dataclasses import dataclass, field


@dataclass
class CodeLocation:
    line: int
    end_line: int | None = None


@dataclass
class ParsedArgument:
    name: str
    annotation: str | None = None


@dataclass
class ParsedFunction:
    name: str
    location: CodeLocation
    args: list[ParsedArgument] = field(default_factory=list)
    return_annotation: str | None = None
    decorators: list[str] = field(default_factory=list)
    docstring: str | None = None
    is_method: bool = False
    is_async: bool = False
    is_route: bool = False


@dataclass
class ParsedClass:
    name: str
    location: CodeLocation
    bases: list[str] = field(default_factory=list)  # <--- Added inheritance tracking
    methods: list[ParsedFunction] = field(default_factory=list)
    docstring: str | None = None


@dataclass
class ParsedModule:
    name: str
    filepath: str
    docstring: str | None = None  # <--- Added module docstring tracking
    classes: list[ParsedClass] = field(default_factory=list)
    functions: list[ParsedFunction] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
