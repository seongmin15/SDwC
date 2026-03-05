"""Phase 8 models: Evolution, Rollout, Operations (WHAT-NEXT)."""

from pydantic import BaseModel

from sdwc_api.schemas.enums import PlannedPhase, RolloutStrategy

# --- Evolution ---


class FutureFeature(BaseModel):
    """Planned future feature."""

    feature: str
    planned_phase: PlannedPhase
    architectural_impact: str
    preparation_needed: str


class Evolution(BaseModel):
    """Project evolution plan."""

    future_features: list[FutureFeature] | None = None
    migration_path: str | None = None
    sunset_criteria: str | None = None


# --- Rollout ---


class RolloutPhase(BaseModel):
    """Rollout phase definition."""

    phase: str
    audience: str
    success_criteria: str


class Rollout(BaseModel):
    """Rollout plan."""

    strategy: RolloutStrategy | None = None
    phases: list[RolloutPhase] | None = None
    rollback_plan: str | None = None
    db_migration_strategy: str | None = None


# --- Operations ---


class Operations(BaseModel):
    """Operations configuration."""

    on_call_policy: str | None = None
    incident_response: str | None = None
    maintenance_window: str | None = None
    documentation_maintenance: str | None = None
