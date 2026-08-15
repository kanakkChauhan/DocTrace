from dataclasses import dataclass, field

from backend.domain.ast_models import CodeLocation


@dataclass
class TraceLink:
    claim_id: str
    code_element_type: str  # "module", "class", "function", "method"
    code_element_name: str  # Fully qualified: "user_repository.UserRepository.get_user"
    filepath: str
    location: CodeLocation
    match_type: str  # "strong" or "weak"
    match_score: float  # 0.0 to 1.0
    evidence: list[str] = field(default_factory=list)
    status: str = "pending"  # "pending", "verified", "rejected"
