"""Tests for Phase 8 models: Evolution, Rollout, Operations."""

import pytest
from pydantic import ValidationError

from sdwc_api.schemas.phase8 import (
    Evolution,
    FutureFeature,
    Operations,
    Rollout,
    RolloutPhase,
)

# --- Evolution ---


class TestEvolution:
    def test_create_with_all_optional_defaults(self) -> None:
        e = Evolution()
        assert e.future_features is None
        assert e.migration_path is None
        assert e.sunset_criteria is None

    def test_create_with_all_fields_succeeds(self) -> None:
        e = Evolution(
            future_features=[
                FutureFeature(
                    feature="Multi-language support",
                    planned_phase="v2",
                    architectural_impact="Template engine must support i18n",
                    preparation_needed="Design i18n key structure",
                ),
            ],
            migration_path="v1 -> v2 with backward compatibility",
            sunset_criteria="No active users for 6 months",
        )
        assert len(e.future_features) == 1
        assert e.future_features[0].planned_phase == "v2"

    def test_invalid_planned_phase_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            FutureFeature(
                feature="x",
                planned_phase="alpha",  # type: ignore[arg-type]
                architectural_impact="x",
                preparation_needed="x",
            )
        assert "planned_phase" in str(exc_info.value)


# --- Rollout ---


class TestRollout:
    def test_create_with_all_optional_defaults(self) -> None:
        r = Rollout()
        assert r.strategy is None
        assert r.phases is None
        assert r.rollback_plan is None
        assert r.db_migration_strategy is None

    def test_create_with_all_fields_succeeds(self) -> None:
        r = Rollout(
            strategy="canary",
            phases=[
                RolloutPhase(
                    phase="Beta",
                    audience="Internal team",
                    success_criteria="No critical bugs for 1 week",
                ),
                RolloutPhase(
                    phase="GA",
                    audience="All users",
                    success_criteria="99.9% uptime for 1 month",
                ),
            ],
            rollback_plan="Revert to previous Docker image",
            db_migration_strategy="forward-only with alembic",
        )
        assert r.strategy == "canary"
        assert len(r.phases) == 2

    def test_invalid_rollout_strategy_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Rollout(strategy="yolo")  # type: ignore[arg-type]
        assert "strategy" in str(exc_info.value)


# --- Operations ---


class TestOperations:
    def test_create_with_all_optional_defaults(self) -> None:
        o = Operations()
        assert o.on_call_policy is None
        assert o.incident_response is None
        assert o.maintenance_window is None
        assert o.documentation_maintenance is None

    def test_create_with_all_fields_succeeds(self) -> None:
        o = Operations(
            on_call_policy="Weekly rotation",
            incident_response="PagerDuty -> Slack -> War room",
            maintenance_window="Sunday 2-4 AM UTC",
            documentation_maintenance="Review quarterly",
        )
        assert o.on_call_policy == "Weekly rotation"
