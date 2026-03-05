"""Integration tests for intake template and validation endpoints."""

import pytest
import yaml
from httpx import AsyncClient


def _minimal_intake_yaml() -> bytes:
    """Return minimal valid intake YAML as bytes."""
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
    ).encode("utf-8")


class TestGetTemplate:
    @pytest.mark.integration
    async def test_returns_200_with_yaml_content_type(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/template")

        assert response.status_code == 200
        assert "application/x-yaml" in response.headers["content-type"]

    @pytest.mark.integration
    async def test_response_contains_yaml_template(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/template")

        body = response.text
        assert "project:" in body
        assert "services:" in body

    @pytest.mark.integration
    async def test_content_disposition_has_filename(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/template")

        assert "intake_template.yaml" in response.headers.get("content-disposition", "")


class TestPostValidate:
    @pytest.mark.integration
    async def test_valid_yaml_returns_valid_true(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/validate",
            files={"file": ("intake_data.yaml", _minimal_intake_yaml(), "application/x-yaml")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["errors"] == []
        assert data["warnings"] == []

    @pytest.mark.integration
    async def test_invalid_yaml_syntax_returns_error(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/validate",
            files={"file": ("bad.yaml", b"invalid: yaml: [unterminated", "application/x-yaml")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) == 1
        assert "Invalid YAML" in data["errors"][0]["detail"]
        assert data["errors"][0]["status"] == 422

    @pytest.mark.integration
    async def test_missing_required_fields_returns_field_errors(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/validate",
            files={"file": ("partial.yaml", b"project:\n  name: Test", "application/x-yaml")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0
        assert all(e["type"] == "https://sdwc.dev/errors/validation-failed" for e in data["errors"])

    @pytest.mark.integration
    async def test_empty_file_returns_error(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/validate",
            files={"file": ("empty.yaml", b"", "application/x-yaml")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) == 1

    @pytest.mark.integration
    async def test_oversized_file_returns_error(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/validate",
            files={"file": ("big.yaml", b"x" * (1_048_576 + 1), "application/x-yaml")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "exceeds maximum" in data["errors"][0]["detail"]

    @pytest.mark.integration
    async def test_error_items_follow_rfc7807_format(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/validate",
            files={"file": ("bad.yaml", b"not: valid", "application/x-yaml")},
        )

        data = response.json()
        assert data["valid"] is False
        error = data["errors"][0]
        assert error["type"] == "https://sdwc.dev/errors/validation-failed"
        assert error["title"] == "Validation Failed"
        assert error["status"] == 422
        assert error["instance"] == "/api/v1/validate"
        assert "detail" in error

    @pytest.mark.integration
    async def test_no_file_returns_422(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/validate")

        assert response.status_code == 422
