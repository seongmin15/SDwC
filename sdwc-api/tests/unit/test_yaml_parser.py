"""Tests for YAML parser: valid parsing, size limit, invalid YAML, timeout, validation errors."""

import pytest
import yaml

from sdwc_api.exceptions import YamlParseError
from sdwc_api.services.yaml_parser import parse_intake_yaml


def _minimal_intake_yaml() -> str:
    """Return minimal valid intake YAML string."""
    return yaml.dump(
        {
            "project": {"name": "Test", "one_liner": "Test project", "elevator_pitch": "A test"},
            "problem": {
                "statement": "Testing",
                "who_has_this_problem": "Devs",
                "severity": "high",
                "frequency": "daily",
                "current_workaround": "None",
                "workaround_pain_points": ["Slow"],
            },
            "motivation": {"why_now": "Need it"},
            "value_proposition": {"core_value": "Fast", "unique_differentiator": "YAML"},
            "goals": {
                "primary": [{"goal": "Test", "measurable_criterion": "Pass", "priority": "P0"}],
                "success_scenario": "All tests pass",
            },
            "non_goals": [{"statement": "Not this", "rationale": "Out of scope"}],
            "scope": {
                "in_scope": [{"feature": "Parse", "user_story": "As dev", "priority": "must"}],
                "out_of_scope": [{"feature": "GUI", "reason": "Not MVP"}],
            },
            "assumptions": [{"assumption": "YAML works", "if_wrong": "Use JSON"}],
            "user_personas": [
                {"name": "Dev", "description": "Developer", "primary_goal": "Save time", "pain_points": ["Manual"]},
            ],
            "collaboration": {
                "human_developers": 1,
                "review_policy": "review",
                "model_routing": {"primary": "opus"},
                "absolute_rules": ["no secrets"],
                "per_service": [
                    {
                        "service": "test-api",
                        "mode": "autonomous",
                        "test_case_coverage": "basic",
                        "decision_authority": {"claude_autonomous": ["impl"], "requires_approval": ["api"]},
                    },
                ],
            },
            "architecture": {
                "pattern": "monolith",
                "pattern_rationale": "Simple",
                "pattern_alternatives": [
                    {"pattern": "micro", "pros": "Scale", "cons": "Complex", "rejection_reason": "Overkill"},
                ],
            },
            "services": [
                {
                    "name": "test-api",
                    "type": "backend_api",
                    "responsibility": "API",
                    "language": "python",
                    "framework": "fastapi",
                    "build_tool": "poetry",
                    "api_style": "rest",
                    "auth": {"method": "none", "if_none_risks_accepted": "Public"},
                    "endpoints": [{"method": "GET", "path": "/health", "description": "Health"}],
                    "deployment": {"target": "docker_compose"},
                },
            ],
            "critical_flows": [{"flow_name": "Upload", "happy_path": "Parse and validate"}],
            "security": {
                "requirements": [
                    {"category": "input_validation", "requirement": "Validate", "implementation_approach": "Pydantic"},
                ],
            },
            "risks": {
                "technical": [
                    {
                        "risk": "Complexity",
                        "likelihood": "medium",
                        "impact": "high",
                        "mitigation": "Test",
                        "contingency": "Manual",
                    },
                ],
                "irreversible_decisions": [
                    {
                        "decision": "Python",
                        "why_irreversible": "Lock-in",
                        "confidence_level": "high",
                        "reversal_cost": "Rewrite",
                    },
                ],
            },
            "performance": {"expected_concurrent_users": "50"},
            "process": {"methodology": "kanban"},
            "testing": {
                "approach": "test_after",
                "levels": [{"level": "unit", "framework": "pytest"}],
            },
            "version_control": {"branch_strategy": "github_flow"},
        },
        default_flow_style=False,
    )


class TestParseIntakeYaml:
    def test_valid_yaml_succeeds(self) -> None:
        content = _minimal_intake_yaml().encode("utf-8")
        result = parse_intake_yaml(content)
        assert result.project.name == "Test"
        assert result.process.methodology == "kanban"

    def test_oversized_file_raises_yaml_parse_error(self) -> None:
        content = b"x" * (1_048_576 + 1)
        with pytest.raises(YamlParseError, match="exceeds maximum"):
            parse_intake_yaml(content)

    def test_invalid_yaml_raises_yaml_parse_error(self) -> None:
        content = b"invalid: yaml: [unterminated"
        with pytest.raises(YamlParseError, match="Invalid YAML"):
            parse_intake_yaml(content)

    def test_non_mapping_yaml_raises_yaml_parse_error(self) -> None:
        content = b"- just\n- a\n- list"
        with pytest.raises(YamlParseError, match="must be a mapping"):
            parse_intake_yaml(content)

    def test_empty_yaml_raises_yaml_parse_error(self) -> None:
        content = b""
        with pytest.raises(YamlParseError, match="must be a mapping"):
            parse_intake_yaml(content)

    def test_invalid_utf8_raises_yaml_parse_error(self) -> None:
        content = b"\xff\xfe invalid utf8"
        with pytest.raises(YamlParseError, match="Invalid"):
            parse_intake_yaml(content)

    def test_pydantic_validation_error_propagates(self) -> None:
        """Missing required fields should raise Pydantic ValidationError."""
        from pydantic import ValidationError

        content = b"project:\n  name: Test"
        with pytest.raises(ValidationError):
            parse_intake_yaml(content)

    def test_valid_yaml_with_optional_phases(self) -> None:
        """Valid YAML with optional phase 8 fields should succeed."""
        yaml_str = _minimal_intake_yaml()
        data = yaml.safe_load(yaml_str)
        data["evolution"] = {
            "future_features": [
                {
                    "feature": "i18n",
                    "planned_phase": "v2",
                    "architectural_impact": "Templates",
                    "preparation_needed": "Key structure",
                },
            ],
        }
        data["rollout"] = {"strategy": "canary"}
        data["operations"] = {"on_call_policy": "Weekly rotation"}
        content = yaml.dump(data, default_flow_style=False).encode("utf-8")
        result = parse_intake_yaml(content)
        assert result.evolution is not None
        assert result.rollout is not None
        assert result.operations is not None

    def test_yaml_parse_error_is_sdwc_error_subclass(self) -> None:
        """YamlParseError should be a subclass of SdwcError."""
        from sdwc_api.exceptions import SdwcError

        content = b"x" * (1_048_576 + 1)
        with pytest.raises(SdwcError):
            parse_intake_yaml(content)
