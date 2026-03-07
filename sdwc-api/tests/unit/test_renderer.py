"""Tests for engine.renderer: Jinja2 rendering pipeline."""

from pathlib import Path

import pytest

from sdwc_api.engine.renderer import (
    _discover_templates,
    _make_adr_seq,
    _map_output_path,
    create_jinja_env,
    render_all,
)
from sdwc_api.exceptions import FrameworkNotFoundError, SdwcError
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

# --- Helpers ---


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


def _minimal_web_service(**overrides: object) -> WebUiService:
    defaults: dict = {
        "name": "my-web",
        "type": "web_ui",
        "responsibility": "Web UI",
        "language": "typescript",
        "framework": "react",
        "build_tool": "vite",
        "pages": [Page(name="Home", purpose="Main", connected_endpoints=[])],
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
    """Build minimal IntakeData with one backend service."""
    svc = overrides.pop("services") if "services" in overrides else [_minimal_backend_service()]
    svc_names = [s.name for s in svc]  # type: ignore[union-attr]
    per_svcs = (
        overrides.pop("per_service_list")
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
                {
                    "risk": "Complexity",
                    "likelihood": "medium",
                    "impact": "high",
                    "mitigation": "Test",
                    "contingency": "Manual",
                },
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


def _create_template_dir(
    tmp_path: Path,
    *,
    claude_base: str | None = None,
    common_docs: dict[str, str] | None = None,
    service_type_docs: dict[str, dict[str, str]] | None = None,
    common_skills: dict[str, str] | None = None,
    framework_skills: dict[str, dict[str, str]] | None = None,
) -> Path:
    """Build a minimal template directory structure under tmp_path.

    Args:
        claude_base: Content for CLAUDE_BASE.md.
        common_docs: {filename: content} for doc-templates/common/.
        service_type_docs: {service_type: {filename: content}} for doc-templates/{type}/.
        common_skills: {folder/SKILL.md: content} for skill-templates/common/.
        framework_skills: {framework: {folder/SKILL.md: content}} for skill-templates/per-framework/{fw}/.
    """
    tpl_dir = tmp_path / "templates"
    tpl_dir.mkdir()

    if claude_base is not None:
        (tpl_dir / "CLAUDE_BASE.md").write_text(claude_base)

    if common_docs:
        d = tpl_dir / "doc-templates" / "common"
        d.mkdir(parents=True)
        for name, content in common_docs.items():
            (d / name).write_text(content)

    if service_type_docs:
        for svc_type, files in service_type_docs.items():
            d = tpl_dir / "doc-templates" / svc_type
            d.mkdir(parents=True)
            for name, content in files.items():
                (d / name).write_text(content)

    if common_skills:
        for rel_path, content in common_skills.items():
            p = tpl_dir / "skill-templates" / "common" / rel_path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)

    if framework_skills:
        for fw, files in framework_skills.items():
            for rel_path, content in files.items():
                p = tpl_dir / "skill-templates" / "per-framework" / fw / rel_path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)

    return tpl_dir


# ===== TestAdrSeq =====


class TestAdrSeq:
    def test_starts_at_one(self) -> None:
        seq = _make_adr_seq()
        assert seq() == 1

    def test_sequential_increment(self) -> None:
        seq = _make_adr_seq()
        assert seq() == 1
        assert seq() == 2
        assert seq() == 3

    def test_independent_closures(self) -> None:
        """Two closures count independently."""
        seq1 = _make_adr_seq()
        seq2 = _make_adr_seq()
        assert seq1() == 1
        assert seq1() == 2
        assert seq2() == 1  # independent

    def test_resets_per_fresh_closure(self) -> None:
        """Fresh closure always starts at 1."""
        seq = _make_adr_seq()
        seq()
        seq()
        seq()
        new_seq = _make_adr_seq()
        assert new_seq() == 1


# ===== TestMapOutputPath =====


class TestMapOutputPath:
    def test_claude_base(self) -> None:
        assert _map_output_path("CLAUDE_BASE.md") == "CLAUDE.md"

    def test_common_doc(self) -> None:
        assert _map_output_path("doc-templates/common/00-overview.md") == "docs/common/00-overview.md"

    def test_service_doc(self) -> None:
        result = _map_output_path("doc-templates/backend_api/20-data-design.md", "my-api")
        assert result == "docs/my-api/20-data-design.md"

    def test_common_skill(self) -> None:
        assert _map_output_path("skill-templates/common/git/SKILL.md") == "skills/common/git/SKILL.md"

    def test_per_framework_skill(self) -> None:
        result = _map_output_path("skill-templates/per-framework/fastapi/coding-standards/SKILL.md", "my-api")
        assert result == "skills/my-api/coding-standards/SKILL.md"


# ===== TestDiscoverTemplates =====


class TestDiscoverTemplates:
    def test_finds_md_files(self, tmp_path: Path) -> None:
        tpl_dir = _create_template_dir(tmp_path, common_docs={"01-req.md": "x", "02-arch.md": "y"})
        result = _discover_templates(tpl_dir, "doc-templates/common")
        assert len(result) == 2

    def test_sorted_order(self, tmp_path: Path) -> None:
        tpl_dir = _create_template_dir(tmp_path, common_docs={"02-arch.md": "y", "01-req.md": "x"})
        result = _discover_templates(tpl_dir, "doc-templates/common")
        assert result[0].endswith("01-req.md")
        assert result[1].endswith("02-arch.md")

    def test_empty_dir_returns_empty(self, tmp_path: Path) -> None:
        tpl_dir = _create_template_dir(tmp_path)
        result = _discover_templates(tpl_dir, "doc-templates/common")
        assert result == []

    def test_nonexistent_dir_returns_empty(self, tmp_path: Path) -> None:
        tpl_dir = tmp_path / "nope"
        result = _discover_templates(tpl_dir, "doc-templates/common")
        assert result == []

    def test_recursive_discovery(self, tmp_path: Path) -> None:
        tpl_dir = _create_template_dir(
            tmp_path,
            common_skills={"git/SKILL.md": "git", "observability/SKILL.md": "obs"},
        )
        result = _discover_templates(tpl_dir, "skill-templates/common")
        assert len(result) == 2
        assert all("/" in p for p in result)

    def test_forward_slashes(self, tmp_path: Path) -> None:
        """All returned paths use forward slashes (Windows safety)."""
        tpl_dir = _create_template_dir(tmp_path, common_docs={"01-req.md": "x"})
        result = _discover_templates(tpl_dir, "doc-templates/common")
        for p in result:
            assert "\\" not in p


# ===== TestCreateJinjaEnv =====


class TestCreateJinjaEnv:
    def test_trim_lstrip_blocks(self, tmp_path: Path) -> None:
        """trim_blocks and lstrip_blocks clean up Markdown output."""
        (tmp_path / "test.md").write_text("{% if true %}\nHello\n{% endif %}\n")
        env = create_jinja_env(tmp_path)
        result = env.get_template("test.md").render()
        assert result == "Hello\n"

    def test_undefined_renders_empty(self, tmp_path: Path) -> None:
        """Undefined variables render as empty string (for {{ mermaid_erd }} etc.)."""
        (tmp_path / "test.md").write_text("Before{{ mermaid_erd }}After\n")
        env = create_jinja_env(tmp_path)
        result = env.get_template("test.md").render()
        assert result == "BeforeAfter\n"

    def test_trailing_newline_preserved(self, tmp_path: Path) -> None:
        (tmp_path / "test.md").write_text("Hello\n")
        env = create_jinja_env(tmp_path)
        result = env.get_template("test.md").render()
        assert result.endswith("\n")


# ===== TestRenderAll =====


class TestRenderAll:
    def test_claude_md_rendered(self, tmp_path: Path) -> None:
        tpl_dir = _create_template_dir(
            tmp_path,
            claude_base="# {{ project.name }}\n",
            framework_skills={"fastapi": {"s/SKILL.md": "ok\n"}},
        )
        intake = _minimal_intake()
        result = render_all(intake, tpl_dir)
        assert "CLAUDE.md" in result
        assert "TestProj" in result["CLAUDE.md"]

    def test_common_docs_rendered(self, tmp_path: Path) -> None:
        tpl_dir = _create_template_dir(
            tmp_path,
            common_docs={"00-overview.md": "# {{ project.name }}\n"},
            framework_skills={"fastapi": {"s/SKILL.md": "ok\n"}},
        )
        intake = _minimal_intake()
        result = render_all(intake, tpl_dir)
        assert "docs/common/00-overview.md" in result
        assert "TestProj" in result["docs/common/00-overview.md"]

    def test_service_docs_rendered(self, tmp_path: Path) -> None:
        tpl_dir = _create_template_dir(
            tmp_path,
            service_type_docs={"backend_api": {"20-data-design.md": "# {{ name }}\n"}},
            framework_skills={"fastapi": {"coding-standards/SKILL.md": "ok\n"}},
        )
        intake = _minimal_intake()
        result = render_all(intake, tpl_dir)
        assert "docs/my-api/20-data-design.md" in result
        assert "my-api" in result["docs/my-api/20-data-design.md"]

    def test_common_skills_rendered(self, tmp_path: Path) -> None:
        tpl_dir = _create_template_dir(
            tmp_path,
            common_skills={"git/SKILL.md": "# Git for {{ project.name }}\n"},
            framework_skills={"fastapi": {"s/SKILL.md": "ok\n"}},
        )
        intake = _minimal_intake()
        result = render_all(intake, tpl_dir)
        assert "skills/common/git/SKILL.md" in result
        assert "TestProj" in result["skills/common/git/SKILL.md"]

    def test_framework_skills_rendered(self, tmp_path: Path) -> None:
        tpl_dir = _create_template_dir(
            tmp_path,
            framework_skills={"fastapi": {"coding-standards/SKILL.md": "# {{ name }} coding\n"}},
        )
        intake = _minimal_intake()
        result = render_all(intake, tpl_dir)
        assert "skills/my-api/coding-standards/SKILL.md" in result
        assert "my-api" in result["skills/my-api/coding-standards/SKILL.md"]

    def test_multiple_services_separate_outputs(self, tmp_path: Path) -> None:
        api = _minimal_backend_service(name="svc-api")
        web = _minimal_web_service(name="svc-web")
        tpl_dir = _create_template_dir(
            tmp_path,
            service_type_docs={
                "backend_api": {"20-data.md": "{{ name }}\n"},
                "web_ui": {"30-ui.md": "{{ name }}\n"},
            },
            framework_skills={
                "fastapi": {"coding/SKILL.md": "{{ name }}\n"},
                "react": {"coding/SKILL.md": "{{ name }}\n"},
            },
        )
        intake = _minimal_intake(services=[api, web])
        result = render_all(intake, tpl_dir)
        assert "docs/svc-api/20-data.md" in result
        assert "docs/svc-web/30-ui.md" in result
        assert "svc-api" in result["docs/svc-api/20-data.md"]
        assert "svc-web" in result["docs/svc-web/30-ui.md"]

    def test_service_context_root_level_fields(self, tmp_path: Path) -> None:
        """Service docs use {{ name }} not {{ services[0].name }}."""
        tpl_dir = _create_template_dir(
            tmp_path,
            service_type_docs={"backend_api": {"doc.md": "{{ name }}-{{ framework }}\n"}},
            framework_skills={"fastapi": {"s/SKILL.md": "ok\n"}},
        )
        intake = _minimal_intake()
        result = render_all(intake, tpl_dir)
        assert "my-api-fastapi" in result["docs/my-api/doc.md"]

    def test_skill_context_has_mode_and_coverage(self, tmp_path: Path) -> None:
        """Skill templates can access {{ mode }} and {{ test_case_coverage }}."""
        tpl_dir = _create_template_dir(
            tmp_path,
            framework_skills={"fastapi": {"testing/SKILL.md": "{{ mode }}-{{ test_case_coverage }}\n"}},
        )
        intake = _minimal_intake()
        result = render_all(intake, tpl_dir)
        assert "autonomous-standard" in result["skills/my-api/testing/SKILL.md"]

    def test_missing_framework_raises_error(self, tmp_path: Path) -> None:
        """Missing framework directory raises FrameworkNotFoundError."""
        tpl_dir = _create_template_dir(tmp_path)  # No framework_skills
        intake = _minimal_intake()
        with pytest.raises(FrameworkNotFoundError) as exc_info:
            render_all(intake, tpl_dir)
        assert exc_info.value.framework == "fastapi"
        assert exc_info.value.service_name == "my-api"

    def test_framework_not_found_is_sdwc_error(self) -> None:
        """FrameworkNotFoundError is a subclass of SdwcError."""
        assert issubclass(FrameworkNotFoundError, SdwcError)

    def test_adr_seq_in_template(self, tmp_path: Path) -> None:
        tpl_dir = _create_template_dir(
            tmp_path,
            common_docs={"02-arch.md": "ADR-{{ adr_seq() }} ADR-{{ adr_seq() }}\n"},
            framework_skills={"fastapi": {"s/SKILL.md": "ok\n"}},
        )
        intake = _minimal_intake()
        result = render_all(intake, tpl_dir)
        assert "ADR-1 ADR-2" in result["docs/common/02-arch.md"]

    def test_adr_seq_resets_between_calls(self, tmp_path: Path) -> None:
        """adr_seq restarts at 1 for each render_all call."""
        tpl_dir = _create_template_dir(
            tmp_path,
            common_docs={"02-arch.md": "ADR-{{ adr_seq() }}\n"},
            framework_skills={"fastapi": {"s/SKILL.md": "ok\n"}},
        )
        intake = _minimal_intake()
        result1 = render_all(intake, tpl_dir)
        result2 = render_all(intake, tpl_dir)
        assert "ADR-1" in result1["docs/common/02-arch.md"]
        assert "ADR-1" in result2["docs/common/02-arch.md"]

    def test_forward_slashes_in_output_keys(self, tmp_path: Path) -> None:
        """All output keys use forward slashes."""
        tpl_dir = _create_template_dir(
            tmp_path,
            claude_base="ok\n",
            common_docs={"01-req.md": "ok\n"},
            common_skills={"git/SKILL.md": "ok\n"},
            framework_skills={"fastapi": {"coding/SKILL.md": "ok\n"}},
        )
        intake = _minimal_intake()
        result = render_all(intake, tpl_dir)
        for key in result:
            assert "\\" not in key, f"Backslash in output key: {key}"

    def test_empty_template_dir(self, tmp_path: Path) -> None:
        """Empty template dir with no framework skills raises FrameworkNotFoundError."""
        tpl_dir = tmp_path / "templates"
        tpl_dir.mkdir()
        intake = _minimal_intake()
        with pytest.raises(FrameworkNotFoundError):
            render_all(intake, tpl_dir)

    def test_no_claude_base_skipped(self, tmp_path: Path) -> None:
        """If CLAUDE_BASE.md doesn't exist, CLAUDE.md is not in output."""
        tpl_dir = _create_template_dir(
            tmp_path,
            framework_skills={"fastapi": {"coding/SKILL.md": "ok\n"}},
        )
        intake = _minimal_intake()
        result = render_all(intake, tpl_dir)
        assert "CLAUDE.md" not in result
