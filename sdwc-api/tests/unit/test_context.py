"""Tests for engine.context: normalize and compose functions."""

import copy

from sdwc_api.engine.context import (
    compose_global_context,
    compose_service_context,
    compose_skill_context,
    normalize,
)
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

# --- Helpers ---


def _minimal_backend_service(**overrides: object) -> BackendApiService:
    """Build a minimal valid BackendApiService."""
    defaults: dict = {
        "name": "sdwc-api",
        "type": "backend_api",
        "responsibility": "API server",
        "language": "python",
        "framework": "fastapi",
        "build_tool": "poetry",
        "api_style": "rest",
        "auth": Auth(method="none", if_none_risks_accepted="Public utility"),
        "deployment": Deployment(target="docker_compose"),
    }
    defaults.update(overrides)
    return BackendApiService(**defaults)


def _minimal_web_service(**overrides: object) -> WebUiService:
    """Build a minimal valid WebUiService."""
    defaults: dict = {
        "name": "sdwc-web",
        "type": "web_ui",
        "responsibility": "Web interface",
        "language": "typescript",
        "framework": "react",
        "build_tool": "vite",
        "pages": [Page(name="Home", purpose="Main page")],
        "page_transitions": [{"from": "Home", "to": "Result", "condition": "submit"}],
        "deployment": Deployment(target="docker_compose"),
    }
    defaults.update(overrides)
    return WebUiService(**defaults)


def _minimal_per_service(service_name: str = "sdwc-api", **overrides: object) -> PerServiceCollaboration:
    """Build a minimal valid PerServiceCollaboration."""
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


def _minimal_intake_data(**overrides: object) -> IntakeData:
    """Build a minimal valid IntakeData instance."""
    data: dict = {
        "project": Project(name="SDwC", one_liner="Doc gen", elevator_pitch="Generate docs"),
        "problem": Problem(
            statement="Manual docs",
            who_has_this_problem="Devs",
            severity="high",
            frequency="daily",
            current_workaround="Write manually",
            workaround_pain_points=["Slow"],
        ),
        "motivation": Motivation(why_now="Claude Code needs context"),
        "value_proposition": ValueProposition(core_value="Automated docs", unique_differentiator="YAML-driven"),
        "goals": Goals(
            primary=[{"goal": "Generate docs", "measurable_criterion": "100%", "priority": "P0"}],
            success_scenario="Docs generated",
        ),
        "non_goals": [NonGoal(statement="GUI editor", rationale="Out of scope")],
        "scope": Scope(
            in_scope=[{"feature": "YAML parsing", "user_story": "Upload YAML", "priority": "must"}],
            out_of_scope=[{"feature": "GUI editor", "reason": "Not MVP"}],
        ),
        "assumptions": [Assumption(assumption="YAML is sufficient", if_wrong="Support JSON")],
        "user_personas": [
            UserPersona(name="Solo Dev", description="Solo developer", primary_goal="Save time", pain_points=["Slow"]),
        ],
        "collaboration": Collaboration(
            human_developers=1,
            review_policy="review after every task",
            model_routing={"primary": "opus"},
            absolute_rules=["no hardcoded secrets"],
            per_service=[
                {
                    "service": "sdwc-api",
                    "mode": "autonomous",
                    "test_case_coverage": "standard",
                    "decision_authority": {
                        "claude_autonomous": ["implementation details"],
                        "requires_approval": ["new endpoints"],
                    },
                },
            ],
        ),
        "architecture": Architecture(
            pattern="monolith",
            pattern_rationale="Simple",
            pattern_alternatives=[
                {"pattern": "microservices", "pros": "Scale", "cons": "Complex", "rejection_reason": "Overkill"},
            ],
        ),
        "services": [_minimal_backend_service()],
        "critical_flows": [CriticalFlow(flow_name="Upload YAML", happy_path="Parse and validate")],
        "security": Security(
            requirements=[
                {"category": "input_validation", "requirement": "Validate YAML", "implementation_approach": "Pydantic"},
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
                }
            ],
            irreversible_decisions=[
                {
                    "decision": "Python",
                    "why_irreversible": "Ecosystem",
                    "confidence_level": "high",
                    "reversal_cost": "Rewrite",
                }
            ],
        ),
        "performance": Performance(expected_concurrent_users="50"),
        "process": Process(methodology="kanban"),
        "testing": Testing(approach="test_after", levels=[{"level": "unit", "framework": "pytest"}]),
        "version_control": VersionControl(branch_strategy="github_flow"),
    }
    data.update(overrides)
    return IntakeData(**data)


# ===== TestNormalize =====


class TestNormalizeEmptyValues:
    """Test removal of various falsy values."""

    def test_empty_string_removed(self) -> None:
        assert normalize({"a": ""}) == {}

    def test_empty_list_removed(self) -> None:
        assert normalize({"a": []}) == {}

    def test_empty_dict_removed(self) -> None:
        assert normalize({"a": {}}) == {}

    def test_none_removed(self) -> None:
        assert normalize({"a": None}) == {}

    def test_list_of_only_empty_strings_removed(self) -> None:
        assert normalize({"a": ["", ""]}) == {}

    def test_list_with_mixed_empty_strings_filters(self) -> None:
        """Non-empty strings kept, empty strings removed from list."""
        assert normalize({"a": ["x", "", "y"]}) == {"a": ["x", "y"]}


class TestNormalizeProtectedValues:
    """Test that False and 0 are preserved."""

    def test_false_preserved(self) -> None:
        result = normalize({"flag": False})
        assert result == {"flag": False}

    def test_zero_preserved(self) -> None:
        result = normalize({"count": 0})
        assert result == {"count": 0}

    def test_false_in_nested_dict_preserved(self) -> None:
        result = normalize({"outer": {"flag": False}})
        assert result == {"outer": {"flag": False}}

    def test_zero_in_list_preserved(self) -> None:
        result = normalize({"items": [0, 1, 2]})
        assert result == {"items": [0, 1, 2]}


class TestNormalizeRecursive:
    """Test recursive cascade behavior."""

    def test_nested_empty_cascades_to_parent(self) -> None:
        """{"a": {"b": ""}} → {} (child removed, parent becomes empty, removed too)."""
        assert normalize({"a": {"b": ""}}) == {}

    def test_deep_nested_cascade(self) -> None:
        """Three levels deep: all empty → all removed."""
        assert normalize({"a": {"b": {"c": ""}}}) == {}

    def test_partial_cascade_preserves_siblings(self) -> None:
        """Only empty children removed; non-empty siblings preserved."""
        result = normalize({"a": {"b": "", "c": "value"}})
        assert result == {"a": {"c": "value"}}

    def test_false_prevents_parent_removal(self) -> None:
        """Parent with False child is NOT empty → preserved."""
        result = normalize({"a": {"b": "", "flag": False}})
        assert result == {"a": {"flag": False}}

    def test_zero_prevents_parent_removal(self) -> None:
        """Parent with 0 child is NOT empty → preserved."""
        result = normalize({"a": {"x": "", "count": 0}})
        assert result == {"a": {"count": 0}}

    def test_list_of_dicts_where_inner_dicts_become_empty(self) -> None:
        """List items that normalize to empty dicts are removed."""
        result = normalize({"items": [{"a": ""}, {"b": ""}]})
        assert result == {}

    def test_list_of_dicts_mixed(self) -> None:
        """Some dict items empty, some not."""
        result = normalize({"items": [{"a": ""}, {"b": "value"}]})
        assert result == {"items": [{"b": "value"}]}

    def test_observability_example_from_spec(self) -> None:
        """Exact §10.2 observability example: logging.structured=false preserved."""
        data = {
            "observability": {
                "logging": {
                    "framework": "",
                    "structured": False,
                },
                "metrics": {
                    "tool": "",
                    "key_metrics": [],
                },
            },
        }
        result = normalize(data)
        assert result == {
            "observability": {
                "logging": {
                    "structured": False,
                },
            },
        }


class TestNormalizeInputImmutability:
    """Test that normalize does NOT mutate the input."""

    def test_input_not_mutated(self) -> None:
        original = {"a": {"b": "", "c": "value"}, "d": [""]}
        frozen = copy.deepcopy(original)
        normalize(original)
        assert original == frozen

    def test_nested_input_not_mutated(self) -> None:
        original = {"deep": {"nested": {"empty": ""}}}
        frozen = copy.deepcopy(original)
        normalize(original)
        assert original == frozen


# ===== TestComposeGlobalContext =====


class TestComposeGlobalContext:
    def test_top_level_keys_present(self) -> None:
        intake = _minimal_intake_data()
        ctx = compose_global_context(intake)
        assert "project" in ctx
        assert "services" in ctx
        assert "collaboration" in ctx
        assert "process" in ctx

    def test_nested_values_accessible(self) -> None:
        intake = _minimal_intake_data()
        ctx = compose_global_context(intake)
        assert ctx["project"]["name"] == "SDwC"
        assert ctx["process"]["methodology"] == "kanban"

    def test_optional_none_fields_absent(self) -> None:
        intake = _minimal_intake_data()
        ctx = compose_global_context(intake)
        assert "evolution" not in ctx
        assert "rollout" not in ctx
        assert "operations" not in ctx
        assert "timeline" not in ctx

    def test_services_array_present(self) -> None:
        intake = _minimal_intake_data()
        ctx = compose_global_context(intake)
        assert isinstance(ctx["services"], list)
        assert len(ctx["services"]) == 1
        assert ctx["services"][0]["name"] == "sdwc-api"


# ===== TestComposeServiceContext =====


class TestComposeServiceContext:
    def test_root_level_fields(self) -> None:
        svc = _minimal_backend_service()
        ctx = compose_service_context(svc)
        assert ctx["name"] == "sdwc-api"
        assert ctx["type"] == "backend_api"
        assert ctx["language"] == "python"

    def test_optional_none_removed(self) -> None:
        svc = _minimal_backend_service()
        ctx = compose_service_context(svc)
        # framework_rationale is optional and not set
        assert "framework_rationale" not in ctx
        assert "framework_alternatives" not in ctx

    def test_by_alias_verified_page_transition(self) -> None:
        """PageTransition.from_page serializes as 'from' with by_alias=True."""
        svc = _minimal_web_service()
        ctx = compose_service_context(svc)
        transition = ctx["page_transitions"][0]
        assert "from" in transition
        assert "from_page" not in transition
        assert transition["from"] == "Home"

    def test_nested_deployment_present(self) -> None:
        svc = _minimal_backend_service()
        ctx = compose_service_context(svc)
        assert "deployment" in ctx
        assert ctx["deployment"]["target"] == "docker_compose"

    def test_web_service_pages(self) -> None:
        svc = _minimal_web_service()
        ctx = compose_service_context(svc)
        assert isinstance(ctx["pages"], list)
        assert ctx["pages"][0]["name"] == "Home"


# ===== TestComposeSkillContext =====


class TestComposeSkillContext:
    def test_service_fields_present(self) -> None:
        svc = _minimal_backend_service()
        ps = _minimal_per_service("sdwc-api")
        ctx = compose_skill_context(svc, ps)
        assert ctx["name"] == "sdwc-api"
        assert ctx["framework"] == "fastapi"

    def test_collaboration_fields_present(self) -> None:
        svc = _minimal_backend_service()
        ps = _minimal_per_service("sdwc-api")
        ctx = compose_skill_context(svc, ps)
        assert ctx["mode"] == "autonomous"
        assert ctx["test_case_coverage"] == "standard"

    def test_service_key_removed(self) -> None:
        """The 'service' name-matcher key from PerServiceCollaboration is removed."""
        svc = _minimal_backend_service()
        ps = _minimal_per_service("sdwc-api")
        ctx = compose_skill_context(svc, ps)
        assert "service" not in ctx

    def test_decision_authority_accessible(self) -> None:
        svc = _minimal_backend_service()
        ps = _minimal_per_service("sdwc-api")
        ctx = compose_skill_context(svc, ps)
        assert "decision_authority" in ctx
        assert "claude_autonomous" in ctx["decision_authority"]
        assert "requires_approval" in ctx["decision_authority"]

    def test_normalized_after_merge(self) -> None:
        """Optional None fields from both sources should be removed."""
        svc = _minimal_backend_service()
        ps = _minimal_per_service("sdwc-api", human_roles=None, claude_roles=None)
        ctx = compose_skill_context(svc, ps)
        assert "human_roles" not in ctx
        assert "claude_roles" not in ctx
        # Service optional fields also absent
        assert "framework_rationale" not in ctx
