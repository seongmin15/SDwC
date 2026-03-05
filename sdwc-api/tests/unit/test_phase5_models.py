"""Tests for Phase 5 models: Critical Flows, Security, Risks, Error Handling."""

import pytest
from pydantic import ValidationError

from sdwc_api.schemas.phase5 import (
    AcceptedSecurityRisk,
    CriticalFlow,
    FailureScenario,
    GlobalErrorHandling,
    IrreversibleDecision,
    Risks,
    Security,
    SecurityRequirement,
    TechnicalDebt,
    TechnicalRisk,
    Threat,
)


# --- CriticalFlow ---


class TestCriticalFlow:
    def test_create_with_required_fields_succeeds(self) -> None:
        cf = CriticalFlow(flow_name="Upload YAML", happy_path="User uploads valid YAML")
        assert cf.failure_scenarios is None

    def test_create_with_failure_scenarios_succeeds(self) -> None:
        cf = CriticalFlow(
            flow_name="Upload YAML",
            happy_path="User uploads valid YAML",
            failure_scenarios=[
                FailureScenario(
                    scenario="Invalid YAML syntax",
                    likelihood="high",
                    impact="low",
                    handling_strategy="Show parse error with line number",
                ),
            ],
        )
        assert len(cf.failure_scenarios) == 1

    def test_invalid_likelihood_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            FailureScenario(
                scenario="x",
                likelihood="very_high",
                impact="low",
                handling_strategy="x",
            )
        assert "likelihood" in str(exc_info.value)

    def test_invalid_impact_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            FailureScenario(
                scenario="x",
                likelihood="high",
                impact="critical",
                handling_strategy="x",
            )
        assert "impact" in str(exc_info.value)


# --- GlobalErrorHandling ---


class TestGlobalErrorHandling:
    def test_create_with_all_optional_defaults(self) -> None:
        geh = GlobalErrorHandling()
        assert geh.retry_policy is None
        assert geh.circuit_breaker is None

    def test_create_with_all_fields_succeeds(self) -> None:
        geh = GlobalErrorHandling(
            retry_policy="3 retries with exponential backoff",
            circuit_breaker="Open after 5 failures",
            graceful_degradation="Return cached data",
            dead_letter_queue="Failed messages to DLQ",
        )
        assert geh.retry_policy is not None


# --- Security ---


class TestSecurity:
    def test_create_with_required_fields_succeeds(self) -> None:
        s = Security(
            requirements=[
                SecurityRequirement(
                    category="input_validation",
                    requirement="Validate all user input",
                    implementation_approach="Pydantic models",
                ),
            ],
        )
        assert len(s.requirements) == 1
        assert s.threat_model is None

    def test_create_with_all_fields_succeeds(self) -> None:
        s = Security(
            requirements=[
                SecurityRequirement(
                    category="transport_security",
                    requirement="HTTPS only",
                    implementation_approach="TLS termination at LB",
                ),
            ],
            input_validation_strategy="Pydantic at API boundary",
            threat_model=[Threat(threat="XSS", mitigation="Input sanitization")],
            compliance_requirements=["GDPR"],
            accepted_security_risks=[
                AcceptedSecurityRisk(
                    risk="No auth",
                    acceptance_rationale="Public utility",
                    reconsider_when="PII is added",
                ),
            ],
        )
        assert len(s.threat_model) == 1

    def test_empty_requirements_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Security(requirements=[])
        assert "requirements" in str(exc_info.value)

    def test_invalid_security_category_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            SecurityRequirement(
                category="firewall",
                requirement="x",
                implementation_approach="x",
            )
        assert "category" in str(exc_info.value)


# --- Risks ---


class TestRisks:
    def test_create_with_required_fields_succeeds(self) -> None:
        r = Risks(
            technical=[
                TechnicalRisk(
                    risk="Template complexity",
                    likelihood="medium",
                    impact="high",
                    mitigation="Incremental testing",
                    contingency="Manual editing fallback",
                ),
            ],
            irreversible_decisions=[
                IrreversibleDecision(
                    decision="Python 3.12",
                    why_irreversible="Ecosystem lock-in",
                    confidence_level="high",
                    reversal_cost="Full rewrite",
                ),
            ],
        )
        assert r.known_technical_debt is None

    def test_create_with_technical_debt_succeeds(self) -> None:
        r = Risks(
            technical=[
                TechnicalRisk(
                    risk="x",
                    likelihood="low",
                    impact="low",
                    mitigation="x",
                    contingency="x",
                ),
            ],
            irreversible_decisions=[
                IrreversibleDecision(
                    decision="x",
                    why_irreversible="x",
                    confidence_level="medium",
                    reversal_cost="x",
                ),
            ],
            known_technical_debt=[
                TechnicalDebt(debt="No caching", reason="MVP scope", resolution_plan="Add in v2"),
            ],
        )
        assert len(r.known_technical_debt) == 1

    def test_empty_technical_risks_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Risks(
                technical=[],
                irreversible_decisions=[
                    IrreversibleDecision(
                        decision="x",
                        why_irreversible="x",
                        confidence_level="high",
                        reversal_cost="x",
                    ),
                ],
            )
        assert "technical" in str(exc_info.value)

    def test_empty_irreversible_decisions_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Risks(
                technical=[
                    TechnicalRisk(
                        risk="x",
                        likelihood="high",
                        impact="high",
                        mitigation="x",
                        contingency="x",
                    ),
                ],
                irreversible_decisions=[],
            )
        assert "irreversible_decisions" in str(exc_info.value)

    def test_invalid_confidence_level_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            IrreversibleDecision(
                decision="x",
                why_irreversible="x",
                confidence_level="certain",
                reversal_cost="x",
            )
        assert "confidence_level" in str(exc_info.value)
