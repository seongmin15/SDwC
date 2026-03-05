"""Phase 2 models: Goals and Scope (WHAT)."""

from pydantic import BaseModel, Field

from sdwc_api.schemas.enums import (
    ComplexityEstimate,
    ConstraintSource,
    GoalPriority,
    Negotiable,
    PlannedPhase,
    ScopePriority,
    TimelineFlexibility,
)


class Goal(BaseModel):
    """A single project goal."""

    goal: str
    measurable_criterion: str
    priority: GoalPriority


class SuccessMetric(BaseModel):
    """Quantitative success metric."""

    metric: str
    current_value: str
    target_value: str
    measurement_method: str


class Goals(BaseModel):
    """Project goals and success criteria."""

    primary: list[Goal] = Field(min_length=1)
    success_scenario: str
    success_metrics: list[SuccessMetric] | None = None


class NonGoal(BaseModel):
    """Explicit non-goal to prevent scope creep."""

    statement: str
    rationale: str
    reconsider_when: str | None = None


class InScopeFeature(BaseModel):
    """Feature included in project scope."""

    feature: str
    user_story: str
    priority: ScopePriority
    complexity_estimate: ComplexityEstimate | None = None


class OutOfScopeFeature(BaseModel):
    """Feature excluded from current scope."""

    feature: str
    reason: str
    planned_phase: PlannedPhase | None = None


class Scope(BaseModel):
    """Project scope boundaries."""

    in_scope: list[InScopeFeature] = Field(min_length=1)
    out_of_scope: list[OutOfScopeFeature] = Field(min_length=1)


class Assumption(BaseModel):
    """Project assumption with risk assessment."""

    assumption: str
    if_wrong: str
    validation_plan: str | None = None


class Constraint(BaseModel):
    """Project constraint."""

    constraint: str
    source: ConstraintSource | None = None
    negotiable: Negotiable | None = None


class Timeline(BaseModel):
    """Project timeline."""

    deadline: str | None = None
    reason: str | None = None
    flexibility: TimelineFlexibility | None = None


class Budget(BaseModel):
    """Project budget."""

    monthly_budget: str | None = None
    one_time_budget: str | None = None
    constraint_items: list[str] | None = None


class GlossaryEntry(BaseModel):
    """Domain term definition."""

    term: str
    definition: str
    aliases: str | None = None
    example: str | None = None
