"""Tests for root IntakeData model and cross-field validation."""

import pytest
from pydantic import ValidationError

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


def _minimal_intake_data(**overrides: object) -> dict:
    """Build minimal valid IntakeData dict. Override any top-level field."""
    data: dict = {
        # Phase 1
        "project": Project(name="SDwC", one_liner="Doc gen", elevator_pitch="Generate docs from YAML"),
        "problem": Problem(
            statement="Manual docs",
            who_has_this_problem="Developers",
            severity="high",
            frequency="daily",
            current_workaround="Write manually",
            workaround_pain_points=["Slow"],
        ),
        "motivation": Motivation(why_now="Claude Code needs context"),
        "value_proposition": ValueProposition(core_value="Automated docs", unique_differentiator="YAML-driven"),
        # Phase 2
        "goals": Goals(
            primary=[{"goal": "Generate docs", "measurable_criterion": "100% coverage", "priority": "P0"}],
            success_scenario="Docs generated correctly",
        ),
        "non_goals": [NonGoal(statement="GUI editor", rationale="Out of scope")],
        "scope": Scope(
            in_scope=[{"feature": "YAML parsing", "user_story": "As dev, upload YAML", "priority": "must"}],
            out_of_scope=[{"feature": "GUI editor", "reason": "Not MVP"}],
        ),
        "assumptions": [Assumption(assumption="YAML is sufficient", if_wrong="Support JSON")],
        # Phase 3
        "user_personas": [
            UserPersona(
                name="Solo Dev",
                description="Solo developer",
                primary_goal="Save time",
                pain_points=["Manual docs"],
            ),
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
        # Phase 4
        "architecture": Architecture(
            pattern="monolith",
            pattern_rationale="Simple",
            pattern_alternatives=[
                {"pattern": "microservices", "pros": "Scale", "cons": "Complex", "rejection_reason": "Overkill"},
            ],
        ),
        "services": [
            BackendApiService(
                name="sdwc-api",
                type="backend_api",
                responsibility="API",
                language="python",
                framework="fastapi",
                build_tool="poetry",
                api_style="rest",
                auth=Auth(method="none", if_none_risks_accepted="Public"),
                endpoints=[Endpoint(method="POST", path="/generate", description="Generate docs")],
                deployment=Deployment(target="docker_compose"),
            ),
        ],
        # Phase 5
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
        # Phase 6
        "performance": Performance(expected_concurrent_users="50"),
        # Phase 7
        "process": Process(methodology="kanban"),
        "testing": Testing(
            approach="test_after",
            levels=[{"level": "unit", "framework": "pytest"}],
        ),
        "version_control": VersionControl(branch_strategy="github_flow"),
    }
    data.update(overrides)
    return data


class TestIntakeData:
    def test_create_with_minimal_valid_data_succeeds(self) -> None:
        intake = IntakeData(**_minimal_intake_data())
        assert intake.project.name == "SDwC"
        assert intake.process.methodology == "kanban"
        assert intake.evolution is None
        assert intake.rollout is None
        assert intake.operations is None

    def test_missing_required_field_raises_error(self) -> None:
        data = _minimal_intake_data()
        del data["project"]
        with pytest.raises(ValidationError) as exc_info:
            IntakeData(**data)
        assert "project" in str(exc_info.value)

    def test_missing_performance_raises_error(self) -> None:
        data = _minimal_intake_data()
        del data["performance"]
        with pytest.raises(ValidationError) as exc_info:
            IntakeData(**data)
        assert "performance" in str(exc_info.value)

    def test_missing_process_raises_error(self) -> None:
        data = _minimal_intake_data()
        del data["process"]
        with pytest.raises(ValidationError) as exc_info:
            IntakeData(**data)
        assert "process" in str(exc_info.value)


class TestIntakeDataCrossValidation:
    def test_per_service_matches_services_succeeds(self) -> None:
        """per_service[].service == services[].name should pass."""
        intake = IntakeData(**_minimal_intake_data())
        assert len(intake.services) == 1
        assert intake.collaboration.per_service[0].service == "sdwc-api"

    def test_per_service_missing_service_raises_error(self) -> None:
        """per_service references a service not in services[]."""
        data = _minimal_intake_data()
        data["collaboration"] = Collaboration(
            human_developers=1,
            review_policy="review",
            model_routing={"primary": "opus"},
            absolute_rules=["no secrets"],
            per_service=[
                {
                    "service": "nonexistent-svc",
                    "mode": "autonomous",
                    "test_case_coverage": "basic",
                    "decision_authority": {
                        "claude_autonomous": ["x"],
                        "requires_approval": ["y"],
                    },
                },
            ],
        )
        with pytest.raises(ValidationError) as exc_info:
            IntakeData(**data)
        assert "per_service must match services 1:1" in str(exc_info.value)

    def test_per_service_extra_entry_raises_error(self) -> None:
        """per_service has an entry that doesn't exist in services[]."""
        data = _minimal_intake_data()
        data["collaboration"] = Collaboration(
            human_developers=1,
            review_policy="review",
            model_routing={"primary": "opus"},
            absolute_rules=["no secrets"],
            per_service=[
                {
                    "service": "sdwc-api",
                    "mode": "autonomous",
                    "test_case_coverage": "basic",
                    "decision_authority": {
                        "claude_autonomous": ["x"],
                        "requires_approval": ["y"],
                    },
                },
                {
                    "service": "extra-svc",
                    "mode": "learning",
                    "test_case_coverage": "basic",
                    "decision_authority": {
                        "claude_autonomous": ["x"],
                        "requires_approval": ["y"],
                    },
                },
            ],
        )
        with pytest.raises(ValidationError) as exc_info:
            IntakeData(**data)
        assert "per_service must match services 1:1" in str(exc_info.value)

    def test_per_service_subset_of_services_raises_error(self) -> None:
        """services[] has entries not covered by per_service[]."""
        from sdwc_api.schemas.phase4_services import Page, WebUiService

        data = _minimal_intake_data()
        # Add a second service but keep per_service with only one entry
        web_svc = WebUiService(
            name="sdwc-web",
            type="web_ui",
            responsibility="UI",
            language="typescript",
            framework="react",
            build_tool="vite",
            pages=[Page(name="Home", purpose="Main page", connected_endpoints=[])],
            deployment=Deployment(target="docker_compose"),
        )
        data["services"] = [*list(data["services"]), web_svc]
        with pytest.raises(ValidationError) as exc_info:
            IntakeData(**data)
        assert "per_service must match services 1:1" in str(exc_info.value)
        assert "sdwc-web" in str(exc_info.value)
