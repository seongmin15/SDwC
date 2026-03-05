"""Phase 1 models: Project Identity (WHY)."""

from pydantic import BaseModel, Field

from sdwc_api.schemas.enums import Frequency, Severity


class Project(BaseModel):
    """Project basic identity."""

    name: str
    codename: str | None = None
    one_liner: str
    elevator_pitch: str


class Problem(BaseModel):
    """Problem definition the project solves."""

    statement: str
    who_has_this_problem: str
    severity: Severity
    frequency: Frequency
    current_workaround: str
    workaround_pain_points: list[str] = Field(min_length=1)
    prior_attempts: str | None = None


class Motivation(BaseModel):
    """Why the project is being built now."""

    why_now: str
    trigger_event: str | None = None
    opportunity_cost: str | None = None
    competitive_landscape: str | None = None
    inspiration_references: list[str] | None = None


class ValueProposition(BaseModel):
    """Core value and differentiator."""

    core_value: str
    unique_differentiator: str
    value_hypothesis: str | None = None


class ProjectCharacteristic(BaseModel):
    """Project characteristic that affects Claude's behavior."""

    label: str
    description: str
