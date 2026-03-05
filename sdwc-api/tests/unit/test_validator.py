"""Tests for engine.validator: output contract validation."""

from __future__ import annotations

import pytest

from sdwc_api.engine.validator import (
    _check_c1,
    _check_c2,
    _check_c3,
    _check_c4,
    _check_c5,
    _check_c6,
    _check_c7,
    _check_s2,
    _check_s3,
    _check_s4,
    _check_s5,
    _check_s6,
    _check_s7,
    _check_s8,
    _check_s9,
    validate_or_raise,
    validate_output,
)
from sdwc_api.exceptions import OutputContractError
from sdwc_api.schemas.intake import IntakeData
from sdwc_api.schemas.phase1 import (
    Motivation,
    Problem,
    Project,
    ValueProposition,
)
from sdwc_api.schemas.phase2 import (
    Assumption,
    Goals,
    NonGoal,
    Scope,
)
from sdwc_api.schemas.phase3 import (
    Collaboration,
    DecisionAuthority,
    PerServiceCollaboration,
    UserPersona,
)
from sdwc_api.schemas.phase4_architecture import Architecture
from sdwc_api.schemas.phase4_services import (
    Auth,
    BackendApiService,
    Deployment,
    Page,
    WebUiService,
)
from sdwc_api.schemas.phase5 import (
    CriticalFlow,
    Risks,
    Security,
)
from sdwc_api.schemas.phase6 import Performance
from sdwc_api.schemas.phase7 import (
    Process,
    Testing,
    VersionControl,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CONTENT = "# Title\n\nSome content here.\n"


def _minimal_backend_service(**overrides: object) -> BackendApiService:
    defaults: dict = {
        "name": "my-api",
        "type": "backend_api",
        "responsibility": "API server",
        "language": "python",
        "framework": "fastapi",
        "build_tool": "poetry",
        "api_style": "rest",
        "auth": Auth(method="none", if_none_risks_accepted="Public"),
        "deployment": Deployment(target="docker_compose"),
    }
    defaults.update(overrides)
    return BackendApiService(**defaults)


def _minimal_web_service(**overrides: object) -> WebUiService:
    defaults: dict = {
        "name": "my-web",
        "type": "web_ui",
        "responsibility": "Web UI",
        "language": "typescript",
        "framework": "react",
        "build_tool": "vite",
        "pages": [Page(name="Home", purpose="Main")],
        "page_transitions": [{"from": "Home", "to": "Result", "condition": "submit"}],
        "deployment": Deployment(target="docker_compose"),
    }
    defaults.update(overrides)
    return WebUiService(**defaults)


def _minimal_per_service(service_name: str, **overrides: object) -> PerServiceCollaboration:
    defaults: dict = {
        "service": service_name,
        "mode": "autonomous",
        "test_case_coverage": "standard",
        "decision_authority": DecisionAuthority(
            claude_autonomous=["implementation details"],
            requires_approval=["new endpoints"],
        ),
    }
    defaults.update(overrides)
    return PerServiceCollaboration(**defaults)


def _minimal_intake(**overrides: object) -> IntakeData:
    svc = overrides.pop("services") if "services" in overrides else [_minimal_backend_service()]  # type: ignore[arg-type]
    svc_names = [s.name for s in svc]  # type: ignore[union-attr]
    per_svcs = (
        overrides.pop("per_service_list")  # type: ignore[arg-type]
        if "per_service_list" in overrides
        else [_minimal_per_service(n) for n in svc_names]
    )
    data: dict = {
        "project": Project(name="TestProj", one_liner="Test", elevator_pitch="Test project"),
        "problem": Problem(
            statement="Problem",
            who_has_this_problem="Devs",
            severity="high",
            frequency="daily",
            current_workaround="Manual",
            workaround_pain_points=["Slow"],
        ),
        "motivation": Motivation(why_now="Now"),
        "value_proposition": ValueProposition(core_value="Auto", unique_differentiator="YAML"),
        "goals": Goals(
            primary=[{"goal": "Generate", "measurable_criterion": "100%", "priority": "P0"}],
            success_scenario="Done",
        ),
        "non_goals": [NonGoal(statement="GUI", rationale="OOS")],
        "scope": Scope(
            in_scope=[{"feature": "Parse", "user_story": "Upload", "priority": "must"}],
            out_of_scope=[{"feature": "GUI", "reason": "Not MVP"}],
        ),
        "assumptions": [Assumption(assumption="YAML works", if_wrong="JSON")],
        "user_personas": [
            UserPersona(name="Dev", description="Developer", primary_goal="Save time", pain_points=["Slow"]),
        ],
        "collaboration": Collaboration(
            human_developers=1,
            review_policy="review after every task",
            model_routing={"primary": "opus"},
            absolute_rules=["no secrets"],
            per_service=per_svcs,
        ),
        "architecture": Architecture(
            pattern="monolith",
            pattern_rationale="Simple",
            pattern_alternatives=[
                {"pattern": "microservices", "pros": "Scale", "cons": "Complex", "rejection_reason": "Overkill"},
            ],
        ),
        "services": svc,
        "critical_flows": [CriticalFlow(flow_name="Upload", happy_path="Parse")],
        "security": Security(
            requirements=[
                {"category": "input_validation", "requirement": "Validate", "implementation_approach": "Pydantic"},
            ],
        ),
        "risks": Risks(
            technical=[
                {"risk": "None", "likelihood": "low", "impact": "low", "mitigation": "OK", "contingency": "N/A"},
            ],
            irreversible_decisions=[
                {
                    "decision": "Python",
                    "why_irreversible": "Ecosystem",
                    "confidence_level": "high",
                    "reversal_cost": "Rewrite",
                },
            ],
        ),
        "performance": Performance(expected_concurrent_users="50"),
        "process": Process(methodology="kanban"),
        "testing": Testing(approach="test_after", levels=[{"level": "unit", "framework": "pytest"}]),
        "version_control": VersionControl(branch_strategy="github_flow"),
    }
    data.update(overrides)
    return IntakeData(**data)


def _build_valid_rendered(
    services: list[object] | None = None,
) -> dict[str, str]:
    """Build a rendered dict that passes all validation checks."""
    if services is None:
        services = [_minimal_backend_service()]

    result: dict[str, str] = {"CLAUDE.md": _CONTENT}

    # docs/common/ — 12 files
    for path in [
        "docs/common/00-project-overview.md",
        "docs/common/01-requirements.md",
        "docs/common/02-architecture-decisions.md",
        "docs/common/03-quality-plan.md",
        "docs/common/04-infrastructure.md",
        "docs/common/05-roadmap.md",
        "docs/common/06-glossary.md",
        "docs/common/07-workplan.md",
        "docs/common/09-working-log.md",
        "docs/common/10-changelog.md",
        "docs/common/11-troubleshooting.md",
        "docs/common/12-runbook.md",
    ]:
        result[path] = _CONTENT

    # skills/common/ — 3 files
    for path in [
        "skills/common/git/SKILL.md",
        "skills/common/observability/SKILL.md",
        "skills/common/code-comments/SKILL.md",
    ]:
        result[path] = _CONTENT

    svc_docs_map = {
        "backend_api": ["20-data-design.md", "21-api-contract.md"],
        "web_ui": ["30-ui-design.md"],
        "worker": ["40-worker-design.md"],
        "mobile_app": ["50-mobile-design.md"],
        "data_pipeline": ["60-pipeline-design.md"],
    }

    for svc in services:
        name = svc.name  # type: ignore[attr-defined]
        svc_type = svc.type  # type: ignore[attr-defined]
        for doc_file in svc_docs_map.get(svc_type, []):
            result[f"docs/{name}/{doc_file}"] = _CONTENT
        for skill_folder in ["coding-standards", "testing", "framework", "deployment"]:
            result[f"skills/{name}/{skill_folder}/SKILL.md"] = _CONTENT

    return result


# ---------------------------------------------------------------------------
# S-2: CLAUDE.md exists
# ---------------------------------------------------------------------------


class TestCheckS2:
    def test_present(self) -> None:
        rendered = {"CLAUDE.md": _CONTENT}
        assert _check_s2(rendered) == []

    def test_missing(self) -> None:
        rendered: dict[str, str] = {}
        violations = _check_s2(rendered)
        assert len(violations) == 1
        assert "S-2" in violations[0]


# ---------------------------------------------------------------------------
# S-3: docs/common/ has 12 files
# ---------------------------------------------------------------------------


class TestCheckS3:
    def test_all_present(self) -> None:
        rendered = _build_valid_rendered()
        assert _check_s3(rendered) == []

    def test_missing_one(self) -> None:
        rendered = _build_valid_rendered()
        del rendered["docs/common/06-glossary.md"]
        violations = _check_s3(rendered)
        assert len(violations) == 1
        assert "S-3" in violations[0]
        assert "06-glossary" in violations[0]

    def test_extra_file(self) -> None:
        rendered = _build_valid_rendered()
        rendered["docs/common/99-extra.md"] = _CONTENT
        violations = _check_s3(rendered)
        assert len(violations) == 1
        assert "unexpected" in violations[0]


# ---------------------------------------------------------------------------
# S-4: skills/common/ has 3 SKILL.md
# ---------------------------------------------------------------------------


class TestCheckS4:
    def test_all_present(self) -> None:
        rendered = _build_valid_rendered()
        assert _check_s4(rendered) == []

    def test_missing_one(self) -> None:
        rendered = _build_valid_rendered()
        del rendered["skills/common/git/SKILL.md"]
        violations = _check_s4(rendered)
        assert len(violations) == 1
        assert "S-4" in violations[0]

    def test_extra_file(self) -> None:
        rendered = _build_valid_rendered()
        rendered["skills/common/extra/SKILL.md"] = _CONTENT
        violations = _check_s4(rendered)
        assert len(violations) == 1
        assert "unexpected" in violations[0]


# ---------------------------------------------------------------------------
# S-5: Service folder parity
# ---------------------------------------------------------------------------


class TestCheckS5:
    def test_both_present(self) -> None:
        svc = _minimal_backend_service()
        rendered = _build_valid_rendered(services=[svc])
        assert _check_s5(rendered, [svc]) == []

    def test_missing_docs(self) -> None:
        svc = _minimal_backend_service()
        rendered = _build_valid_rendered(services=[svc])
        rendered = {k: v for k, v in rendered.items() if not k.startswith("docs/my-api/")}
        violations = _check_s5(rendered, [svc])
        assert any("docs/my-api/" in v for v in violations)

    def test_missing_skills(self) -> None:
        svc = _minimal_backend_service()
        rendered = _build_valid_rendered(services=[svc])
        rendered = {k: v for k, v in rendered.items() if not k.startswith("skills/my-api/")}
        violations = _check_s5(rendered, [svc])
        assert any("skills/my-api/" in v for v in violations)


# ---------------------------------------------------------------------------
# S-6: Service docs match type
# ---------------------------------------------------------------------------


class TestCheckS6:
    def test_backend_api_correct(self) -> None:
        svc = _minimal_backend_service()
        rendered = _build_valid_rendered(services=[svc])
        assert _check_s6(rendered, [svc]) == []

    def test_web_ui_correct(self) -> None:
        svc = _minimal_web_service()
        rendered = _build_valid_rendered(services=[svc])
        assert _check_s6(rendered, [svc]) == []

    def test_missing_doc_file(self) -> None:
        svc = _minimal_backend_service()
        rendered = _build_valid_rendered(services=[svc])
        del rendered["docs/my-api/20-data-design.md"]
        violations = _check_s6(rendered, [svc])
        assert len(violations) == 1
        assert "20-data-design" in violations[0]

    def test_extra_doc_file(self) -> None:
        svc = _minimal_backend_service()
        rendered = _build_valid_rendered(services=[svc])
        rendered["docs/my-api/99-extra.md"] = _CONTENT
        violations = _check_s6(rendered, [svc])
        assert len(violations) == 1
        assert "unexpected" in violations[0]


# ---------------------------------------------------------------------------
# S-7: Service has 4 skill folders
# ---------------------------------------------------------------------------


class TestCheckS7:
    def test_all_present(self) -> None:
        svc = _minimal_backend_service()
        rendered = _build_valid_rendered(services=[svc])
        assert _check_s7(rendered, [svc]) == []

    def test_missing_one(self) -> None:
        svc = _minimal_backend_service()
        rendered = _build_valid_rendered(services=[svc])
        del rendered["skills/my-api/deployment/SKILL.md"]
        violations = _check_s7(rendered, [svc])
        assert len(violations) == 1
        assert "deployment" in violations[0]

    def test_extra_skill(self) -> None:
        svc = _minimal_backend_service()
        rendered = _build_valid_rendered(services=[svc])
        rendered["skills/my-api/extra/SKILL.md"] = _CONTENT
        violations = _check_s7(rendered, [svc])
        assert len(violations) == 1
        assert "unexpected" in violations[0]


# ---------------------------------------------------------------------------
# S-8: Total file count
# ---------------------------------------------------------------------------


class TestCheckS8:
    def test_correct_count_one_backend(self) -> None:
        svc = _minimal_backend_service()
        rendered = _build_valid_rendered(services=[svc])
        # 16 + 2(backend) + 4*1 = 22
        assert len(rendered) == 22
        assert _check_s8(rendered, [svc]) == []

    def test_correct_count_two_services(self) -> None:
        svcs = [_minimal_backend_service(), _minimal_web_service()]
        rendered = _build_valid_rendered(services=svcs)
        # 16 + 2(backend) + 1(web_ui) + 4*2 = 27
        assert len(rendered) == 27
        assert _check_s8(rendered, svcs) == []

    def test_wrong_count(self) -> None:
        svc = _minimal_backend_service()
        rendered = _build_valid_rendered(services=[svc])
        rendered["extra/file.md"] = _CONTENT
        violations = _check_s8(rendered, [svc])
        assert len(violations) == 1
        assert "S-8" in violations[0]


# ---------------------------------------------------------------------------
# S-9: No empty files
# ---------------------------------------------------------------------------


class TestCheckS9:
    def test_all_non_empty(self) -> None:
        rendered = {"a.md": _CONTENT, "b.md": _CONTENT}
        assert _check_s9(rendered) == []

    def test_empty_file(self) -> None:
        rendered = {"a.md": _CONTENT, "b.md": ""}
        violations = _check_s9(rendered)
        assert len(violations) == 1
        assert "b.md" in violations[0]

    def test_multiple_empty(self) -> None:
        rendered = {"a.md": "", "b.md": "", "c.md": _CONTENT}
        violations = _check_s9(rendered)
        assert len(violations) == 2


# ---------------------------------------------------------------------------
# C-1: No unsubstituted Jinja2
# ---------------------------------------------------------------------------


class TestCheckC1:
    def test_clean(self) -> None:
        rendered = {"a.md": "No templates here"}
        assert _check_c1(rendered) == []

    def test_double_braces(self) -> None:
        rendered = {"a.md": "Hello {{ name }}"}
        violations = _check_c1(rendered)
        assert len(violations) == 1
        assert "C-1" in violations[0]

    def test_closing_braces_only(self) -> None:
        rendered = {"a.md": "result }}"}
        violations = _check_c1(rendered)
        assert len(violations) == 1


# ---------------------------------------------------------------------------
# C-2: ADR numbers consecutive
# ---------------------------------------------------------------------------


class TestCheckC2:
    def test_consecutive(self) -> None:
        content = "### ADR-1: First\n### ADR-2: Second\n### ADR-3: Third\n"
        rendered = {"docs/common/02-architecture-decisions.md": content}
        assert _check_c2(rendered) == []

    def test_gap(self) -> None:
        content = "### ADR-1: First\n### ADR-3: Third\n"
        rendered = {"docs/common/02-architecture-decisions.md": content}
        violations = _check_c2(rendered)
        assert len(violations) == 1
        assert "C-2" in violations[0]

    def test_no_adrs(self) -> None:
        content = "# Architecture Decisions\n\nNo ADRs yet.\n"
        rendered = {"docs/common/02-architecture-decisions.md": content}
        assert _check_c2(rendered) == []

    def test_missing_file(self) -> None:
        rendered: dict[str, str] = {}
        assert _check_c2(rendered) == []


# ---------------------------------------------------------------------------
# C-3: No empty Mermaid blocks
# ---------------------------------------------------------------------------


class TestCheckC3:
    def test_valid_mermaid(self) -> None:
        content = "```mermaid\ngraph TD\nA-->B\n```\n"
        rendered = {"a.md": content}
        assert _check_c3(rendered) == []

    def test_empty_mermaid(self) -> None:
        content = "```mermaid\n```\n"
        rendered = {"a.md": content}
        violations = _check_c3(rendered)
        assert len(violations) == 1
        assert "C-3" in violations[0]

    def test_empty_mermaid_with_whitespace(self) -> None:
        content = "```mermaid\n  \n```\n"
        rendered = {"a.md": content}
        violations = _check_c3(rendered)
        assert len(violations) == 1

    def test_no_mermaid(self) -> None:
        rendered = {"a.md": _CONTENT}
        assert _check_c3(rendered) == []


# ---------------------------------------------------------------------------
# C-4: No empty tables
# ---------------------------------------------------------------------------


class TestCheckC4:
    def test_table_with_data(self) -> None:
        content = "| Col1 | Col2 |\n|------|------|\n| data | data |\n"
        rendered = {"a.md": content}
        assert _check_c4(rendered) == []

    def test_empty_table(self) -> None:
        content = "| Col1 | Col2 |\n|------|------|\n"
        rendered = {"a.md": content}
        violations = _check_c4(rendered)
        assert len(violations) == 1
        assert "C-4" in violations[0]


# ---------------------------------------------------------------------------
# C-5: No empty sections (except Claude-managed)
# ---------------------------------------------------------------------------


class TestCheckC5:
    def test_valid_sections(self) -> None:
        content = "## Section\n\nContent here.\n\n## Next\n\nMore.\n"
        rendered = {"a.md": content}
        assert _check_c5(rendered) == []

    def test_empty_section(self) -> None:
        content = "## Section\n\n## Next\n\nContent.\n"
        rendered = {"a.md": content}
        violations = _check_c5(rendered)
        assert len(violations) == 1
        assert "C-5" in violations[0]

    def test_claude_managed_exempt(self) -> None:
        content = "## Section\n\n## Next\n\nContent.\n"
        rendered = {"docs/common/07-workplan.md": content}
        assert _check_c5(rendered) == []

    def test_claude_managed_09(self) -> None:
        content = "## Section\n\n## Next\n\nContent.\n"
        rendered = {"docs/common/09-working-log.md": content}
        assert _check_c5(rendered) == []


# ---------------------------------------------------------------------------
# C-6: No consecutive dividers
# ---------------------------------------------------------------------------


class TestCheckC6:
    def test_single_divider(self) -> None:
        content = "Above\n\n---\n\nBelow\n"
        rendered = {"a.md": content}
        assert _check_c6(rendered) == []

    def test_consecutive_dividers(self) -> None:
        content = "Above\n\n---\n---\n\nBelow\n"
        rendered = {"a.md": content}
        violations = _check_c6(rendered)
        assert len(violations) == 1
        assert "C-6" in violations[0]


# ---------------------------------------------------------------------------
# C-7: No trailing whitespace
# ---------------------------------------------------------------------------


class TestCheckC7:
    def test_clean(self) -> None:
        content = "Line one\nLine two\n"
        rendered = {"a.md": content}
        assert _check_c7(rendered) == []

    def test_trailing_spaces(self) -> None:
        content = "Line one  \nLine two\n"
        rendered = {"a.md": content}
        violations = _check_c7(rendered)
        assert len(violations) == 1
        assert "C-7" in violations[0]


# ---------------------------------------------------------------------------
# validate_output orchestrator
# ---------------------------------------------------------------------------


class TestValidateOutput:
    def test_all_pass(self) -> None:
        svcs = [_minimal_backend_service()]
        intake = _minimal_intake(services=svcs)
        rendered = _build_valid_rendered(services=svcs)
        assert validate_output(rendered, intake) == []

    def test_two_services_pass(self) -> None:
        svcs = [_minimal_backend_service(), _minimal_web_service()]
        intake = _minimal_intake(services=svcs)
        rendered = _build_valid_rendered(services=svcs)
        assert validate_output(rendered, intake) == []

    def test_multiple_violations_collected(self) -> None:
        svcs = [_minimal_backend_service()]
        intake = _minimal_intake(services=svcs)
        rendered = _build_valid_rendered(services=svcs)
        del rendered["CLAUDE.md"]  # S-2
        rendered["docs/my-api/20-data-design.md"] = ""  # S-9
        violations = validate_output(rendered, intake)
        assert len(violations) >= 2
        check_ids = {v.split(":")[0] for v in violations}
        assert "S-2" in check_ids
        assert "S-9" in check_ids


# ---------------------------------------------------------------------------
# validate_or_raise
# ---------------------------------------------------------------------------


class TestValidateOrRaise:
    def test_passes_cleanly(self) -> None:
        svcs = [_minimal_backend_service()]
        intake = _minimal_intake(services=svcs)
        rendered = _build_valid_rendered(services=svcs)
        validate_or_raise(rendered, intake)  # Should not raise

    def test_raises_on_violation(self) -> None:
        svcs = [_minimal_backend_service()]
        intake = _minimal_intake(services=svcs)
        rendered = _build_valid_rendered(services=svcs)
        del rendered["CLAUDE.md"]
        with pytest.raises(OutputContractError) as exc_info:
            validate_or_raise(rendered, intake)
        assert len(exc_info.value.violations) >= 1
        assert "S-2" in exc_info.value.violations[0]

    def test_error_message_contains_summary(self) -> None:
        svcs = [_minimal_backend_service()]
        intake = _minimal_intake(services=svcs)
        rendered = _build_valid_rendered(services=svcs)
        del rendered["CLAUDE.md"]
        with pytest.raises(OutputContractError, match="output contract violation"):
            validate_or_raise(rendered, intake)
