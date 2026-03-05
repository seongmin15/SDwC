"""Tests for Phase 2 models: Goals and Scope."""

import pytest
from pydantic import ValidationError

from sdwc_api.schemas.phase2 import (
    Assumption,
    Budget,
    Constraint,
    GlossaryEntry,
    Goal,
    Goals,
    InScopeFeature,
    NonGoal,
    OutOfScopeFeature,
    Scope,
    SuccessMetric,
    Timeline,
)


# --- Goal / Goals ---


class TestGoals:
    def test_create_goals_with_valid_data_succeeds(self) -> None:
        g = Goals(
            primary=[
                Goal(goal="Fast docs", measurable_criterion="< 5s generation", priority="P0"),
            ],
            success_scenario="All users generate docs in one try",
        )
        assert len(g.primary) == 1
        assert g.primary[0].priority == "P0"
        assert g.success_metrics is None

    def test_invalid_priority_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Goal(goal="x", measurable_criterion="x", priority="P3")  # type: ignore[arg-type]
        assert "priority" in str(exc_info.value)

    def test_empty_primary_goals_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Goals(primary=[], success_scenario="x")
        assert "primary" in str(exc_info.value)

    def test_goals_with_success_metrics_succeeds(self) -> None:
        g = Goals(
            primary=[Goal(goal="x", measurable_criterion="x", priority="P1")],
            success_scenario="x",
            success_metrics=[
                SuccessMetric(
                    metric="Generation time",
                    current_value="N/A",
                    target_value="< 5s",
                    measurement_method="Timer",
                ),
            ],
        )
        assert len(g.success_metrics) == 1


# --- NonGoal ---


class TestNonGoal:
    def test_create_with_required_fields_succeeds(self) -> None:
        ng = NonGoal(statement="No mobile app", rationale="Web-first")
        assert ng.reconsider_when is None

    def test_create_with_all_fields_succeeds(self) -> None:
        ng = NonGoal(
            statement="No mobile app",
            rationale="Web-first",
            reconsider_when="User demand exceeds 50%",
        )
        assert ng.reconsider_when is not None


# --- Scope ---


class TestScope:
    def test_create_scope_with_valid_data_succeeds(self) -> None:
        s = Scope(
            in_scope=[
                InScopeFeature(
                    feature="YAML upload",
                    user_story="As a dev, I upload YAML",
                    priority="must",
                ),
            ],
            out_of_scope=[
                OutOfScopeFeature(feature="Mobile app", reason="Web-first"),
            ],
        )
        assert len(s.in_scope) == 1
        assert len(s.out_of_scope) == 1

    def test_invalid_scope_priority_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            InScopeFeature(
                feature="x",
                user_story="x",
                priority="wont",  # type: ignore[arg-type]
            )
        assert "priority" in str(exc_info.value)

    def test_invalid_complexity_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            InScopeFeature(
                feature="x",
                user_story="x",
                priority="must",
                complexity_estimate="XXL",  # type: ignore[arg-type]
            )
        assert "complexity_estimate" in str(exc_info.value)

    def test_invalid_planned_phase_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            OutOfScopeFeature(
                feature="x",
                reason="x",
                planned_phase="v4",  # type: ignore[arg-type]
            )
        assert "planned_phase" in str(exc_info.value)

    def test_empty_in_scope_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Scope(
                in_scope=[],
                out_of_scope=[OutOfScopeFeature(feature="x", reason="x")],
            )
        assert "in_scope" in str(exc_info.value)

    def test_empty_out_of_scope_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Scope(
                in_scope=[InScopeFeature(feature="x", user_story="x", priority="must")],
                out_of_scope=[],
            )
        assert "out_of_scope" in str(exc_info.value)


# --- Assumption ---


class TestAssumption:
    def test_create_with_required_fields_succeeds(self) -> None:
        a = Assumption(assumption="Users know YAML", if_wrong="Add GUI editor")
        assert a.validation_plan is None

    def test_create_with_all_fields_succeeds(self) -> None:
        a = Assumption(
            assumption="Users know YAML",
            if_wrong="Add GUI editor",
            validation_plan="Survey users",
        )
        assert a.validation_plan == "Survey users"


# --- Constraint ---


class TestConstraint:
    def test_create_with_required_only_succeeds(self) -> None:
        c = Constraint(constraint="Must run on Python 3.12")
        assert c.source is None
        assert c.negotiable is None

    def test_invalid_source_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Constraint(constraint="x", source="political")  # type: ignore[arg-type]
        assert "source" in str(exc_info.value)

    def test_invalid_negotiable_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Constraint(constraint="x", negotiable="maybe")  # type: ignore[arg-type]
        assert "negotiable" in str(exc_info.value)


# --- Timeline ---


class TestTimeline:
    def test_create_with_all_optional_defaults(self) -> None:
        t = Timeline()
        assert t.deadline is None
        assert t.flexibility is None

    def test_invalid_flexibility_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Timeline(flexibility="soft")  # type: ignore[arg-type]
        assert "flexibility" in str(exc_info.value)


# --- Budget ---


class TestBudget:
    def test_create_with_all_optional_defaults(self) -> None:
        b = Budget()
        assert b.monthly_budget is None

    def test_create_with_all_fields_succeeds(self) -> None:
        b = Budget(
            monthly_budget="$100",
            one_time_budget="$500",
            constraint_items=["Hosting", "Domain"],
        )
        assert len(b.constraint_items) == 2


# --- GlossaryEntry ---


class TestGlossaryEntry:
    def test_create_with_required_fields_succeeds(self) -> None:
        g = GlossaryEntry(term="YAML", definition="Data serialization format")
        assert g.aliases is None
        assert g.example is None

    def test_create_with_all_fields_succeeds(self) -> None:
        g = GlossaryEntry(
            term="YAML",
            definition="Data serialization format",
            aliases="YML",
            example="key: value",
        )
        assert g.aliases == "YML"
