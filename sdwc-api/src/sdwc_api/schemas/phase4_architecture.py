"""Phase 4 models: Architecture (HOW)."""

from pydantic import BaseModel, Field

from sdwc_api.schemas.enums import ArchitecturePattern, InternalStyle


class PatternAlternative(BaseModel):
    """Rejected architecture pattern alternative."""

    pattern: str
    pros: str
    cons: str
    rejection_reason: str


class Architecture(BaseModel):
    """System architecture decisions."""

    pattern: ArchitecturePattern
    pattern_rationale: str
    pattern_alternatives: list[PatternAlternative] = Field(min_length=1)
    internal_style: InternalStyle | None = None
    internal_style_rationale: str | None = None
    principles: list[str] | None = None
