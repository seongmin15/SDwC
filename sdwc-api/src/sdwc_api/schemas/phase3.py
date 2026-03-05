"""Phase 3 models: Users, Stakeholders, and Collaboration (WHO)."""

from pydantic import BaseModel, Field

from sdwc_api.schemas.enums import (
    CollaborationMode,
    InfluenceLevel,
    TechProficiency,
    TestCaseCoverage,
    UsageFrequency,
)


class UserPersona(BaseModel):
    """Target user persona."""

    name: str
    description: str
    primary_goal: str
    pain_points: list[str] = Field(min_length=1)
    is_primary: bool = False
    tech_proficiency: TechProficiency | None = None
    usage_frequency: UsageFrequency | None = None


class AntiPersona(BaseModel):
    """User type explicitly not targeted."""

    name: str
    reason: str


class Stakeholder(BaseModel):
    """Project stakeholder."""

    role: str
    concern: str
    influence_level: InfluenceLevel | None = None


class ModelRouting(BaseModel):
    """AI model routing configuration."""

    primary: str
    secondary: str | None = None
    routing_rule: str | None = None


class DecisionAuthority(BaseModel):
    """Decision authority split between Claude and human."""

    claude_autonomous: list[str] = Field(min_length=1)
    requires_approval: list[str] = Field(min_length=1)


class PerServiceCollaboration(BaseModel):
    """Collaboration settings for a single service.

    CRITICAL: The `mode` field controls how Claude interacts with this service's code.
    """

    service: str
    mode: CollaborationMode
    test_case_coverage: TestCaseCoverage
    decision_authority: DecisionAuthority
    human_roles: list[str] | None = None
    claude_roles: list[str] | None = None
    claude_boundaries: list[str] | None = None


class Collaboration(BaseModel):
    """AI collaboration configuration."""

    human_developers: int
    review_policy: str
    model_routing: ModelRouting
    use_subagent: bool = False
    absolute_rules: list[str] = Field(min_length=1)
    per_service: list[PerServiceCollaboration] = Field(min_length=1)
