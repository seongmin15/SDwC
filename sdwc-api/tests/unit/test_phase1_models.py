"""Tests for Phase 1 models: Project Identity."""

import pytest
from pydantic import ValidationError

from sdwc_api.schemas.phase1 import (
    Motivation,
    Problem,
    Project,
    ProjectCharacteristic,
    ValueProposition,
)


# --- Project ---


class TestProject:
    def test_create_with_required_fields_succeeds(self) -> None:
        p = Project(
            name="SDwC",
            one_liner="Survey-driven documentation generator",
            elevator_pitch="Fill a YAML survey, get a complete doc package.",
        )
        assert p.name == "SDwC"
        assert p.codename is None

    def test_create_with_all_fields_succeeds(self) -> None:
        p = Project(
            name="SDwC",
            codename="docgen",
            one_liner="Survey-driven documentation generator",
            elevator_pitch="Fill a YAML survey, get a complete doc package.",
        )
        assert p.codename == "docgen"

    def test_missing_required_field_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Project(name="SDwC", one_liner="short")  # type: ignore[call-arg]
        assert "elevator_pitch" in str(exc_info.value)


# --- Problem ---


class TestProblem:
    def test_create_with_valid_data_succeeds(self) -> None:
        p = Problem(
            statement="Docs take too long",
            who_has_this_problem="Solo developers",
            severity="high",
            frequency="daily",
            current_workaround="Manual writing",
            workaround_pain_points=["Slow", "Inconsistent"],
        )
        assert p.severity == "high"
        assert len(p.workaround_pain_points) == 2

    def test_invalid_severity_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Problem(
                statement="x",
                who_has_this_problem="x",
                severity="critical",  # type: ignore[arg-type]
                frequency="daily",
                current_workaround="x",
                workaround_pain_points=["x"],
            )
        assert "severity" in str(exc_info.value)

    def test_invalid_frequency_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Problem(
                statement="x",
                who_has_this_problem="x",
                severity="high",
                frequency="yearly",  # type: ignore[arg-type]
                current_workaround="x",
                workaround_pain_points=["x"],
            )
        assert "frequency" in str(exc_info.value)

    def test_empty_pain_points_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Problem(
                statement="x",
                who_has_this_problem="x",
                severity="high",
                frequency="daily",
                current_workaround="x",
                workaround_pain_points=[],
            )
        assert "workaround_pain_points" in str(exc_info.value)

    def test_optional_prior_attempts_defaults_none(self) -> None:
        p = Problem(
            statement="x",
            who_has_this_problem="x",
            severity="low",
            frequency="occasional",
            current_workaround="x",
            workaround_pain_points=["x"],
        )
        assert p.prior_attempts is None


# --- Motivation ---


class TestMotivation:
    def test_create_with_required_only_succeeds(self) -> None:
        m = Motivation(why_now="Market opportunity")
        assert m.why_now == "Market opportunity"
        assert m.trigger_event is None
        assert m.inspiration_references is None

    def test_create_with_all_fields_succeeds(self) -> None:
        m = Motivation(
            why_now="Market opportunity",
            trigger_event="Conference talk",
            opportunity_cost="Lost users",
            competitive_landscape="No competitors",
            inspiration_references=["Tool A", "Tool B"],
        )
        assert len(m.inspiration_references) == 2


# --- ValueProposition ---


class TestValueProposition:
    def test_create_with_required_fields_succeeds(self) -> None:
        vp = ValueProposition(
            core_value="Automated docs",
            unique_differentiator="YAML-driven",
        )
        assert vp.value_hypothesis is None

    def test_missing_required_field_raises_error(self) -> None:
        with pytest.raises(ValidationError):
            ValueProposition(core_value="x")  # type: ignore[call-arg]


# --- ProjectCharacteristic ---


class TestProjectCharacteristic:
    def test_create_succeeds(self) -> None:
        pc = ProjectCharacteristic(label="Stateless", description="No database")
        assert pc.label == "Stateless"

    def test_missing_field_raises_error(self) -> None:
        with pytest.raises(ValidationError):
            ProjectCharacteristic(label="Stateless")  # type: ignore[call-arg]
