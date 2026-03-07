"""Root IntakeData model combining all phases."""

from pydantic import BaseModel, Field, model_validator

from sdwc_api.schemas.phase1 import (
    Motivation,
    Problem,
    Project,
    ProjectCharacteristic,
    ValueProposition,
)
from sdwc_api.schemas.phase2 import (
    Assumption,
    Budget,
    Constraint,
    GlossaryEntry,
    Goals,
    NonGoal,
    Scope,
    Timeline,
)
from sdwc_api.schemas.phase3 import (
    AntiPersona,
    Collaboration,
    Stakeholder,
    UserPersona,
)
from sdwc_api.schemas.phase4_architecture import Architecture
from sdwc_api.schemas.phase4_services import Service
from sdwc_api.schemas.phase5 import (
    CriticalFlow,
    GlobalErrorHandling,
    Risks,
    Security,
)
from sdwc_api.schemas.phase6 import (
    Availability,
    ExternalSystem,
    Observability,
    Performance,
    Scalability,
)
from sdwc_api.schemas.phase7 import (
    CodeQuality,
    Process,
    Testing,
    VersionControl,
)
from sdwc_api.schemas.phase8 import Evolution, Operations, Rollout


class IntakeData(BaseModel):
    """Root model for the complete intake YAML.

    Combines all phases (1-8) into a single validated structure.
    """

    # Phase 1
    project: Project
    problem: Problem
    motivation: Motivation
    value_proposition: ValueProposition
    project_characteristics: list[ProjectCharacteristic] | None = None

    # Phase 2
    goals: Goals
    non_goals: list[NonGoal] = Field(min_length=1)
    scope: Scope
    assumptions: list[Assumption] = Field(min_length=1)
    constraints: list[Constraint] | None = None
    timeline: Timeline | None = None
    budget: Budget | None = None
    glossary: list[GlossaryEntry] | None = None

    # Phase 3
    user_personas: list[UserPersona] = Field(min_length=1)
    anti_personas: list[AntiPersona] | None = None
    stakeholders: list[Stakeholder] | None = None
    collaboration: Collaboration

    # Phase 4
    architecture: Architecture
    services: list[Service] = Field(min_length=1)

    # Phase 5
    critical_flows: list[CriticalFlow] = Field(min_length=1)
    global_error_handling: GlobalErrorHandling | None = None
    data_consistency: str | None = None
    security: Security
    risks: Risks

    # Phase 6
    performance: Performance
    availability: Availability | None = None
    observability: Observability | None = None
    scalability: Scalability | None = None
    external_systems: list[ExternalSystem] | None = None

    # Phase 7
    process: Process
    code_quality: CodeQuality | None = None
    testing: Testing
    version_control: VersionControl

    # Phase 8
    evolution: Evolution | None = None
    rollout: Rollout | None = None
    operations: Operations | None = None

    @model_validator(mode="after")
    def validate_per_service_matches_services(self) -> "IntakeData":
        """Validate that collaboration.per_service[].service matches services[].name 1:1."""
        service_names = {s.name for s in self.services}
        per_service_names = {ps.service for ps in self.collaboration.per_service}

        if service_names != per_service_names:
            missing_in_collab = service_names - per_service_names
            extra_in_collab = per_service_names - service_names
            parts: list[str] = []
            if missing_in_collab:
                parts.append(f"services missing in collaboration.per_service: {sorted(missing_in_collab)}")
            if extra_in_collab:
                parts.append(f"extra in collaboration.per_service not in services: {sorted(extra_in_collab)}")
            raise ValueError(f"collaboration.per_service must match services 1:1. {'; '.join(parts)}")
        return self
