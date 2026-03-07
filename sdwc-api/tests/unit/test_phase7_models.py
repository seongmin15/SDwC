"""Tests for Phase 7 models: Process, Code Quality, Testing, Version Control."""

import pytest
from pydantic import ValidationError

from sdwc_api.schemas.phase7 import (
    CodeQuality,
    CodeReview,
    CodingStandard,
    Documentation,
    Process,
    PrPolicy,
    TestEnvironment,
    Testing,
    TestLevelConfig,
    VersionControl,
)

# --- Process ---


class TestProcess:
    def test_create_with_required_fields_succeeds(self) -> None:
        p = Process(methodology="kanban")
        assert p.methodology == "kanban"
        assert p.sprint_length is None
        assert p.wip_limit is None
        assert p.task_review_minutes is None
        assert p.definition_of_done is None

    def test_create_with_all_fields_succeeds(self) -> None:
        p = Process(
            methodology="scrum",
            sprint_length="2 weeks",
            wip_limit="3",
            task_review_minutes="30",
            definition_of_done=["Tests pass", "Docs updated"],
        )
        assert p.sprint_length == "2 weeks"
        assert len(p.definition_of_done) == 2

    def test_invalid_methodology_raises_error(self) -> None:
        """CRITICAL: methodology enum must be strictly validated."""
        with pytest.raises(ValidationError) as exc_info:
            Process(methodology="waterfall")  # type: ignore[arg-type]
        assert "methodology" in str(exc_info.value)

    def test_all_valid_methodology_values(self) -> None:
        for m in ("scrum", "kanban", "scrumban", "xp"):
            p = Process(methodology=m)
            assert p.methodology == m


# --- CodeQuality ---


class TestCodeQuality:
    def test_create_with_all_optional_defaults(self) -> None:
        cq = CodeQuality()
        assert cq.coding_standards is None
        assert cq.code_review is None
        assert cq.documentation is None

    def test_create_with_all_fields_succeeds(self) -> None:
        cq = CodeQuality(
            coding_standards=[
                CodingStandard(
                    language="python",
                    style_guide="PEP 8",
                    linter="ruff",
                    formatter="ruff format",
                ),
            ],
            code_review=CodeReview(
                required=True,
                min_reviewers=1,
                auto_merge_allowed=False,
            ),
            documentation=Documentation(
                code_comments="docstring for public API",
                adr_usage="record major decisions",
                changelog_policy="Keep a Changelog",
            ),
        )
        assert len(cq.coding_standards) == 1
        assert cq.code_review.required is True


class TestCodeReviewDefaults:
    def test_defaults_applied(self) -> None:
        cr = CodeReview()
        assert cr.required is True
        assert cr.min_reviewers == 1
        assert cr.auto_merge_allowed is False

    def test_explicit_values_override_defaults(self) -> None:
        cr = CodeReview(required=False, min_reviewers=2, auto_merge_allowed=True)
        assert cr.required is False
        assert cr.min_reviewers == 2
        assert cr.auto_merge_allowed is True


class TestPrPolicyDefaults:
    def test_defaults_applied(self) -> None:
        pp = PrPolicy()
        assert pp.template_required is True
        assert pp.squash_merge is True
        assert pp.created_by is None

    def test_explicit_values_override_defaults(self) -> None:
        pp = PrPolicy(template_required=False, squash_merge=False, created_by="human")
        assert pp.template_required is False
        assert pp.squash_merge is False


# --- Testing ---


class TestTesting:
    def test_create_with_required_fields_succeeds(self) -> None:
        t = Testing(
            approach="test_after",
            levels=[
                TestLevelConfig(level="unit", framework="pytest"),
            ],
        )
        assert t.approach == "test_after"
        assert t.test_data_strategy is None
        assert t.test_environment is None

    def test_create_with_all_fields_succeeds(self) -> None:
        t = Testing(
            approach="tdd",
            levels=[
                TestLevelConfig(level="unit", framework="pytest", coverage_target="80%"),
                TestLevelConfig(level="e2e", framework="playwright"),
            ],
            test_data_strategy="fixtures",
            test_environment=TestEnvironment(
                db_strategy="in_memory",
                external_service_strategy="mocks",
            ),
        )
        assert len(t.levels) == 2
        assert t.test_data_strategy == "fixtures"

    def test_empty_levels_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Testing(approach="test_after", levels=[])
        assert "levels" in str(exc_info.value)

    def test_invalid_approach_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Testing(
                approach="manual",  # type: ignore[arg-type]
                levels=[TestLevelConfig(level="unit", framework="pytest")],
            )
        assert "approach" in str(exc_info.value)

    def test_invalid_test_level_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            TestLevelConfig(level="acceptance", framework="pytest")  # type: ignore[arg-type]
        assert "level" in str(exc_info.value)

    def test_invalid_test_framework_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            TestLevelConfig(level="unit", framework="mocha")  # type: ignore[arg-type]
        assert "framework" in str(exc_info.value)

    def test_invalid_db_strategy_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            TestEnvironment(db_strategy="production")  # type: ignore[arg-type]
        assert "db_strategy" in str(exc_info.value)

    def test_invalid_external_service_strategy_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            TestEnvironment(external_service_strategy="real")  # type: ignore[arg-type]
        assert "external_service_strategy" in str(exc_info.value)


# --- VersionControl ---


class TestVersionControl:
    def test_create_with_required_fields_succeeds(self) -> None:
        vc = VersionControl(branch_strategy="github_flow")
        assert vc.branch_strategy == "github_flow"
        assert vc.commit_convention is None
        assert vc.monorepo_or_polyrepo is None
        assert vc.pr_policy is None

    def test_create_with_all_fields_succeeds(self) -> None:
        vc = VersionControl(
            branch_strategy="gitflow",
            branch_strategy_description="main + develop + feature branches",
            commit_convention="conventional",
            monorepo_or_polyrepo="monorepo",
            pr_policy=PrPolicy(
                created_by="both",
                template_required=True,
                squash_merge=True,
            ),
        )
        assert vc.pr_policy is not None
        assert vc.pr_policy.created_by == "both"

    def test_invalid_branch_strategy_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            VersionControl(branch_strategy="yolo")  # type: ignore[arg-type]
        assert "branch_strategy" in str(exc_info.value)

    def test_invalid_commit_convention_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            VersionControl(branch_strategy="github_flow", commit_convention="random")  # type: ignore[arg-type]
        assert "commit_convention" in str(exc_info.value)

    def test_invalid_repo_structure_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            VersionControl(branch_strategy="github_flow", monorepo_or_polyrepo="hybrid")  # type: ignore[arg-type]
        assert "monorepo_or_polyrepo" in str(exc_info.value)

    def test_invalid_pr_created_by_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            PrPolicy(created_by="bot")  # type: ignore[arg-type]
        assert "created_by" in str(exc_info.value)
