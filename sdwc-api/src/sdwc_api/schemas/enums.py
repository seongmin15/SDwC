"""Shared enum definitions for intake YAML validation."""

from enum import StrEnum

# Phase 1 enums


class Severity(StrEnum):
    """Problem severity level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Frequency(StrEnum):
    """Problem occurrence frequency."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    OCCASIONAL = "occasional"


# Phase 2 enums


class GoalPriority(StrEnum):
    """Goal priority level."""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class ScopePriority(StrEnum):
    """Feature scope priority (MoSCoW)."""

    MUST = "must"
    SHOULD = "should"
    COULD = "could"


class ComplexityEstimate(StrEnum):
    """Feature complexity T-shirt size."""

    S = "S"
    M = "M"
    L = "L"
    XL = "XL"


class PlannedPhase(StrEnum):
    """Planned implementation phase for out-of-scope features."""

    V2 = "v2"
    V3 = "v3"
    POST_LAUNCH = "post_launch"
    BACKLOG = "backlog"


class ConstraintSource(StrEnum):
    """Source of a project constraint."""

    TECHNICAL = "technical"
    BUSINESS = "business"
    LEGAL = "legal"
    REGULATORY = "regulatory"


class Negotiable(StrEnum):
    """Whether a constraint is negotiable."""

    YES = "yes"
    NO = "no"
    PARTIALLY = "partially"


class TimelineFlexibility(StrEnum):
    """Deadline flexibility level."""

    RIGID = "rigid"
    FLEXIBLE = "flexible"
    ASPIRATIONAL = "aspirational"


# Phase 3 enums


class TechProficiency(StrEnum):
    """User technical proficiency level."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class UsageFrequency(StrEnum):
    """Expected usage frequency."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class InfluenceLevel(StrEnum):
    """Stakeholder influence level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CollaborationMode(StrEnum):
    """AI collaboration mode per service.

    CRITICAL: This enum controls how Claude interacts with the codebase.
    - autonomous: Claude writes code, human reviews.
    - collaborative: Claude and human share responsibilities.
    - learning: Claude only plans/explains, human codes.
    """

    AUTONOMOUS = "autonomous"
    COLLABORATIVE = "collaborative"
    LEARNING = "learning"


class TestCaseCoverage(StrEnum):
    """Test coverage level per service."""

    BASIC = "basic"
    STANDARD = "standard"
    THOROUGH = "thorough"
