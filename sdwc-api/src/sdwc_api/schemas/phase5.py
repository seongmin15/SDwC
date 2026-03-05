"""Phase 5 models: Critical Flows, Security, Risks, Error Handling (WHAT-IF)."""

from pydantic import BaseModel, Field

from sdwc_api.schemas.enums import (
    ConfidenceLevel,
    Impact,
    Likelihood,
    SecurityCategory,
)

# --- Critical Flows ---


class FailureScenario(BaseModel):
    """Possible failure in a critical flow."""

    scenario: str
    likelihood: Likelihood
    impact: Impact
    handling_strategy: str


class CriticalFlow(BaseModel):
    """Critical system flow with failure analysis."""

    flow_name: str
    happy_path: str
    failure_scenarios: list[FailureScenario] | None = None


# --- Error Handling ---


class GlobalErrorHandling(BaseModel):
    """Global error handling strategies."""

    retry_policy: str | None = None
    circuit_breaker: str | None = None
    graceful_degradation: str | None = None
    dead_letter_queue: str | None = None


# --- Security ---


class SecurityRequirement(BaseModel):
    """Security requirement by category."""

    category: SecurityCategory
    requirement: str
    implementation_approach: str


class Threat(BaseModel):
    """Identified threat and its mitigation."""

    threat: str
    mitigation: str


class SensitiveDataHandling(BaseModel):
    """Handling rules for sensitive data."""

    data_type: str
    protection_method: str
    retention_policy: str


class AcceptedSecurityRisk(BaseModel):
    """Consciously accepted security risk."""

    risk: str
    acceptance_rationale: str
    reconsider_when: str


class Security(BaseModel):
    """Security configuration."""

    requirements: list[SecurityRequirement] = Field(min_length=1)
    input_validation_strategy: str | None = None
    threat_model: list[Threat] | None = None
    sensitive_data: list[SensitiveDataHandling] | None = None
    compliance_requirements: list[str] | None = None
    accepted_security_risks: list[AcceptedSecurityRisk] | None = None


# --- Risks ---


class TechnicalRisk(BaseModel):
    """Identified technical risk."""

    risk: str
    likelihood: Likelihood
    impact: Impact
    mitigation: str
    contingency: str


class IrreversibleDecision(BaseModel):
    """Decision that is hard to reverse."""

    decision: str
    why_irreversible: str
    confidence_level: ConfidenceLevel
    reversal_cost: str


class TechnicalDebt(BaseModel):
    """Known technical debt."""

    debt: str
    reason: str
    resolution_plan: str


class Risks(BaseModel):
    """Project risks assessment."""

    technical: list[TechnicalRisk] = Field(min_length=1)
    irreversible_decisions: list[IrreversibleDecision] = Field(min_length=1)
    known_technical_debt: list[TechnicalDebt] | None = None
