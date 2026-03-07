"""Tests for engine.packager: ZIP assembly."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

from sdwc_api.engine.packager import build_zip
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
    Endpoint,
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
        "endpoints": [Endpoint(method="GET", path="/health", description="Health")],
        "deployment": Deployment(target="docker_compose"),
    }
    defaults.update(overrides)
    return BackendApiService(**defaults)


def _minimal_per_service(service_name: str) -> PerServiceCollaboration:
    return PerServiceCollaboration(
        service=service_name,
        mode="autonomous",
        test_case_coverage="standard",
        decision_authority=DecisionAuthority(
            claude_autonomous=["implementation details"],
            requires_approval=["new endpoints"],
        ),
    )


def _minimal_intake(**overrides: object) -> IntakeData:
    svc = overrides.pop("services") if "services" in overrides else [_minimal_backend_service()]  # type: ignore[arg-type]
    svc_names = [s.name for s in svc]  # type: ignore[union-attr]
    per_svcs = [_minimal_per_service(n) for n in svc_names]
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


def _simple_rendered() -> dict[str, str]:
    """A minimal rendered dict for packager tests."""
    return {
        "CLAUDE.md": "# Project\n",
        "docs/common/00-project-overview.md": "# Overview\n",
        "skills/common/git/SKILL.md": "# Git\n",
    }


def _create_template_dir(tmp_path: Path) -> Path:
    """Create a mock .sdwc/ template directory with a few files."""
    tpl_dir = tmp_path / "templates"
    tpl_dir.mkdir()
    (tpl_dir / "intake_template.yaml").write_text("# intake template\n")
    (tpl_dir / "generation_rules.md").write_text("# generation rules\n")
    sub = tpl_dir / "doc-templates" / "common"
    sub.mkdir(parents=True)
    (sub / "00-project-overview.md").write_text("# {{ project.name }}\n")
    return tpl_dir


# ---------------------------------------------------------------------------
# TestBuildZip
# ---------------------------------------------------------------------------


class TestBuildZip:
    def test_returns_bytesio(self, tmp_path: Path) -> None:
        intake = _minimal_intake()
        tpl_dir = _create_template_dir(tmp_path)
        result = build_zip(_simple_rendered(), intake, tpl_dir)
        assert isinstance(result, io.BytesIO)

    def test_valid_zip(self, tmp_path: Path) -> None:
        intake = _minimal_intake()
        tpl_dir = _create_template_dir(tmp_path)
        result = build_zip(_simple_rendered(), intake, tpl_dir)
        assert zipfile.is_zipfile(result)

    def test_root_folder_is_project_name(self, tmp_path: Path) -> None:
        intake = _minimal_intake()
        tpl_dir = _create_template_dir(tmp_path)
        result = build_zip(_simple_rendered(), intake, tpl_dir)
        with zipfile.ZipFile(result, "r") as zf:
            for name in zf.namelist():
                assert name.startswith("TestProj/"), f"File {name} not under root"

    def test_rendered_files_present(self, tmp_path: Path) -> None:
        rendered = _simple_rendered()
        intake = _minimal_intake()
        tpl_dir = _create_template_dir(tmp_path)
        result = build_zip(rendered, intake, tpl_dir)
        with zipfile.ZipFile(result, "r") as zf:
            names = zf.namelist()
            assert "TestProj/CLAUDE.md" in names
            assert "TestProj/docs/common/00-project-overview.md" in names
            assert "TestProj/skills/common/git/SKILL.md" in names

    def test_rendered_content_matches(self, tmp_path: Path) -> None:
        rendered = {"CLAUDE.md": "# My Project\nHello world\n"}
        intake = _minimal_intake()
        tpl_dir = _create_template_dir(tmp_path)
        result = build_zip(rendered, intake, tpl_dir)
        with zipfile.ZipFile(result, "r") as zf:
            content = zf.read("TestProj/CLAUDE.md").decode("utf-8")
            assert content == "# My Project\nHello world\n"

    def test_forward_slashes_in_paths(self, tmp_path: Path) -> None:
        intake = _minimal_intake()
        tpl_dir = _create_template_dir(tmp_path)
        result = build_zip(_simple_rendered(), intake, tpl_dir)
        with zipfile.ZipFile(result, "r") as zf:
            for name in zf.namelist():
                assert "\\" not in name

    def test_seeked_to_zero(self, tmp_path: Path) -> None:
        intake = _minimal_intake()
        tpl_dir = _create_template_dir(tmp_path)
        result = build_zip(_simple_rendered(), intake, tpl_dir)
        assert result.tell() == 0


# ---------------------------------------------------------------------------
# TestSdwcResources
# ---------------------------------------------------------------------------


class TestSdwcResources:
    def test_sdwc_files_present(self, tmp_path: Path) -> None:
        intake = _minimal_intake()
        tpl_dir = _create_template_dir(tmp_path)
        result = build_zip({}, intake, tpl_dir)
        with zipfile.ZipFile(result, "r") as zf:
            names = zf.namelist()
            assert "TestProj/.sdwc/intake_template.yaml" in names
            assert "TestProj/.sdwc/generation_rules.md" in names

    def test_sdwc_content_is_raw(self, tmp_path: Path) -> None:
        """Verify .sdwc/ files are copied raw, not rendered."""
        intake = _minimal_intake()
        tpl_dir = _create_template_dir(tmp_path)
        result = build_zip({}, intake, tpl_dir)
        with zipfile.ZipFile(result, "r") as zf:
            content = zf.read("TestProj/.sdwc/doc-templates/common/00-project-overview.md").decode()
            # Should contain raw Jinja2 syntax, not rendered
            assert "{{ project.name }}" in content

    def test_sdwc_directory_structure_preserved(self, tmp_path: Path) -> None:
        intake = _minimal_intake()
        tpl_dir = _create_template_dir(tmp_path)
        result = build_zip({}, intake, tpl_dir)
        with zipfile.ZipFile(result, "r") as zf:
            names = zf.namelist()
            assert "TestProj/.sdwc/doc-templates/common/00-project-overview.md" in names


# ---------------------------------------------------------------------------
# TestSdwcCopyFailure (E-5)
# ---------------------------------------------------------------------------


class TestSdwcCopyFailure:
    def test_nonexistent_template_dir_logs_warning(self, tmp_path: Path) -> None:
        """ZIP still contains rendered files when template_dir doesn't exist."""
        rendered = _simple_rendered()
        intake = _minimal_intake()
        nonexistent = tmp_path / "does-not-exist"
        result = build_zip(rendered, intake, nonexistent)
        with zipfile.ZipFile(result, "r") as zf:
            names = zf.namelist()
            assert "TestProj/CLAUDE.md" in names
            # No .sdwc/ files since dir doesn't exist
            sdwc_files = [n for n in names if "/.sdwc/" in n]
            assert sdwc_files == []

    def test_empty_template_dir(self, tmp_path: Path) -> None:
        """ZIP is valid even with empty template dir."""
        rendered = _simple_rendered()
        intake = _minimal_intake()
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        result = build_zip(rendered, intake, empty_dir)
        with zipfile.ZipFile(result, "r") as zf:
            names = zf.namelist()
            assert "TestProj/CLAUDE.md" in names
            sdwc_files = [n for n in names if "/.sdwc/" in n]
            assert sdwc_files == []


# ---------------------------------------------------------------------------
# TestZipRootFolder
# ---------------------------------------------------------------------------


class TestZipRootFolder:
    def test_custom_project_name(self, tmp_path: Path) -> None:
        intake = _minimal_intake(
            project=Project(name="MyApp", one_liner="Test", elevator_pitch="Test"),
        )
        tpl_dir = _create_template_dir(tmp_path)
        result = build_zip(_simple_rendered(), intake, tpl_dir)
        with zipfile.ZipFile(result, "r") as zf:
            for name in zf.namelist():
                assert name.startswith("MyApp/")

    def test_hyphenated_name(self, tmp_path: Path) -> None:
        intake = _minimal_intake(
            project=Project(name="my-cool-project", one_liner="Test", elevator_pitch="Test"),
        )
        tpl_dir = _create_template_dir(tmp_path)
        result = build_zip(_simple_rendered(), intake, tpl_dir)
        with zipfile.ZipFile(result, "r") as zf:
            for name in zf.namelist():
                assert name.startswith("my-cool-project/")
