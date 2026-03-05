"""Tests for Phase 3 models: Users, Stakeholders, Collaboration."""

import pytest
from pydantic import ValidationError

from sdwc_api.schemas.phase3 import (
    AntiPersona,
    Collaboration,
    DecisionAuthority,
    ModelRouting,
    PerServiceCollaboration,
    Stakeholder,
    UserPersona,
)


# --- UserPersona ---


class TestUserPersona:
    def test_create_with_required_fields_succeeds(self) -> None:
        up = UserPersona(
            name="Solo Dev",
            description="Works alone on projects",
            primary_goal="Save time on docs",
            pain_points=["Manual doc writing"],
        )
        assert up.is_primary is False
        assert up.tech_proficiency is None

    def test_create_with_all_fields_succeeds(self) -> None:
        up = UserPersona(
            name="Solo Dev",
            description="Works alone",
            primary_goal="Save time",
            pain_points=["Slow", "Boring"],
            is_primary=True,
            tech_proficiency="expert",
            usage_frequency="weekly",
        )
        assert up.is_primary is True
        assert up.tech_proficiency == "expert"

    def test_empty_pain_points_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            UserPersona(
                name="x",
                description="x",
                primary_goal="x",
                pain_points=[],
            )
        assert "pain_points" in str(exc_info.value)

    def test_invalid_tech_proficiency_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            UserPersona(
                name="x",
                description="x",
                primary_goal="x",
                pain_points=["x"],
                tech_proficiency="guru",  # type: ignore[arg-type]
            )
        assert "tech_proficiency" in str(exc_info.value)

    def test_invalid_usage_frequency_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            UserPersona(
                name="x",
                description="x",
                primary_goal="x",
                pain_points=["x"],
                usage_frequency="yearly",  # type: ignore[arg-type]
            )
        assert "usage_frequency" in str(exc_info.value)


# --- AntiPersona ---


class TestAntiPersona:
    def test_create_succeeds(self) -> None:
        ap = AntiPersona(name="Enterprise PM", reason="Too complex for target use case")
        assert ap.name == "Enterprise PM"

    def test_missing_field_raises_error(self) -> None:
        with pytest.raises(ValidationError):
            AntiPersona(name="x")  # type: ignore[call-arg]


# --- Stakeholder ---


class TestStakeholder:
    def test_create_with_required_fields_succeeds(self) -> None:
        s = Stakeholder(role="Product Owner", concern="Delivery timeline")
        assert s.influence_level is None

    def test_invalid_influence_level_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Stakeholder(
                role="x",
                concern="x",
                influence_level="critical",  # type: ignore[arg-type]
            )
        assert "influence_level" in str(exc_info.value)


# --- Collaboration (CRITICAL) ---


def _make_per_service(**overrides: object) -> PerServiceCollaboration:
    """Helper to build a valid PerServiceCollaboration with defaults."""
    defaults: dict[str, object] = {
        "service": "sdwc-api",
        "mode": "autonomous",
        "test_case_coverage": "standard",
        "decision_authority": DecisionAuthority(
            claude_autonomous=["implementation details"],
            requires_approval=["new endpoints"],
        ),
    }
    defaults.update(overrides)
    return PerServiceCollaboration(**defaults)  # type: ignore[arg-type]


def _make_collaboration(**overrides: object) -> Collaboration:
    """Helper to build a valid Collaboration with defaults."""
    defaults: dict[str, object] = {
        "human_developers": 1,
        "review_policy": "review after every task",
        "model_routing": ModelRouting(primary="opus"),
        "absolute_rules": ["no hardcoded secrets"],
        "per_service": [_make_per_service()],
    }
    defaults.update(overrides)
    return Collaboration(**defaults)  # type: ignore[arg-type]


class TestCollaborationMode:
    """CRITICAL: Validate CollaborationMode enum strictly."""

    def test_autonomous_mode_accepted(self) -> None:
        ps = _make_per_service(mode="autonomous")
        assert ps.mode == "autonomous"

    def test_collaborative_mode_accepted(self) -> None:
        ps = _make_per_service(mode="collaborative")
        assert ps.mode == "collaborative"

    def test_learning_mode_accepted(self) -> None:
        ps = _make_per_service(mode="learning")
        assert ps.mode == "learning"

    def test_invalid_mode_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            _make_per_service(mode="supervised")
        assert "mode" in str(exc_info.value)

    def test_empty_mode_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            _make_per_service(mode="")
        assert "mode" in str(exc_info.value)


class TestPerServiceCollaboration:
    def test_create_with_required_fields_succeeds(self) -> None:
        ps = _make_per_service()
        assert ps.service == "sdwc-api"
        assert ps.human_roles is None

    def test_create_with_all_fields_succeeds(self) -> None:
        ps = _make_per_service(
            human_roles=["review"],
            claude_roles=["implement"],
            claude_boundaries=["no DB changes"],
        )
        assert ps.claude_boundaries == ["no DB changes"]

    def test_invalid_test_case_coverage_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            _make_per_service(test_case_coverage="minimal")
        assert "test_case_coverage" in str(exc_info.value)


class TestDecisionAuthority:
    def test_create_with_valid_data_succeeds(self) -> None:
        da = DecisionAuthority(
            claude_autonomous=["impl details"],
            requires_approval=["new endpoints"],
        )
        assert len(da.claude_autonomous) == 1

    def test_empty_claude_autonomous_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            DecisionAuthority(
                claude_autonomous=[],
                requires_approval=["x"],
            )
        assert "claude_autonomous" in str(exc_info.value)

    def test_empty_requires_approval_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            DecisionAuthority(
                claude_autonomous=["x"],
                requires_approval=[],
            )
        assert "requires_approval" in str(exc_info.value)


class TestCollaboration:
    def test_create_with_valid_data_succeeds(self) -> None:
        c = _make_collaboration()
        assert c.human_developers == 1
        assert c.use_subagent is False

    def test_create_with_use_subagent_true_succeeds(self) -> None:
        c = _make_collaboration(use_subagent=True)
        assert c.use_subagent is True

    def test_empty_absolute_rules_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            _make_collaboration(absolute_rules=[])
        assert "absolute_rules" in str(exc_info.value)

    def test_empty_per_service_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            _make_collaboration(per_service=[])
        assert "per_service" in str(exc_info.value)


class TestModelRouting:
    def test_create_with_required_only_succeeds(self) -> None:
        mr = ModelRouting(primary="opus")
        assert mr.secondary is None
        assert mr.routing_rule is None

    def test_create_with_all_fields_succeeds(self) -> None:
        mr = ModelRouting(
            primary="opus",
            secondary="sonnet",
            routing_rule="Opus for complex, Sonnet for routine",
        )
        assert mr.secondary == "sonnet"
