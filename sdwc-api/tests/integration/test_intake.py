"""Integration tests for intake template and validation endpoints."""

import zipfile
from io import BytesIO

import pytest
import yaml
from httpx import AsyncClient


def _minimal_intake_yaml() -> bytes:
    """Return minimal valid intake YAML as bytes (for validation tests)."""
    return yaml.dump(_base_intake_data(), default_flow_style=False).encode("utf-8")


def _renderable_intake_yaml() -> bytes:
    """Return intake YAML with all fields needed for template rendering."""
    data = _base_intake_data()
    # Add optional fields that templates access without null guards
    svc = data["services"][0]
    svc["deployment"].update(
        {
            "ci": {"tool": "github_actions", "pipeline_stages": "lint,test,build"},
            "cd": {"tool": "none", "strategy": "manual"},
            "environments": [{"name": "dev", "purpose": "Development", "differences": "Local only"}],
            "container_registry": "ghcr",
            "secrets_management": "env_file",
        }
    )
    data["version_control"]["commit_convention"] = "conventional"
    return yaml.dump(data, default_flow_style=False).encode("utf-8")


def _base_intake_data() -> dict:  # type: ignore[type-arg]
    """Shared intake data dict."""
    return {
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
                "endpoints": [{"method": "POST", "path": "/generate", "description": "Generate"}],
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
    }


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


class TestGetFieldRequirements:
    @pytest.mark.integration
    async def test_returns_200_with_yaml_content_type(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/field-requirements")

        assert response.status_code == 200
        assert "application/x-yaml" in response.headers["content-type"]

    @pytest.mark.integration
    async def test_response_contains_valid_yaml_with_phases(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/field-requirements")

        data = yaml.safe_load(response.text)
        assert data["version"] == "1.0"
        assert "phases" in data
        assert "phase1_why" in data["phases"]

    @pytest.mark.integration
    async def test_content_disposition_has_filename(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/field-requirements")

        assert "field_requirements.yaml" in response.headers.get("content-disposition", "")


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


class TestPostPreview:
    @pytest.mark.integration
    async def test_valid_yaml_returns_preview(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/preview",
            files={"file": ("intake.yaml", _renderable_intake_yaml(), "application/x-yaml")},
        )

        assert response.status_code == 200
        data = response.json()
        assert "file_tree" in data
        assert "file_count" in data
        assert "services" in data
        assert data["file_count"] > 0

    @pytest.mark.integration
    async def test_file_tree_contains_claude_md(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/preview",
            files={"file": ("intake.yaml", _renderable_intake_yaml(), "application/x-yaml")},
        )

        data = response.json()
        assert "CLAUDE.md" in data["file_tree"]

    @pytest.mark.integration
    async def test_services_match_intake(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/preview",
            files={"file": ("intake.yaml", _renderable_intake_yaml(), "application/x-yaml")},
        )

        data = response.json()
        services = data["services"]
        assert len(services) == 1
        assert services[0]["name"] == "test-api"
        assert services[0]["type"] == "backend_api"
        assert services[0]["framework"] == "fastapi"

    @pytest.mark.integration
    async def test_invalid_yaml_returns_error(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/preview",
            files={"file": ("bad.yaml", b"invalid: yaml: [unterminated", "application/x-yaml")},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    async def test_no_file_returns_422(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/preview")

        assert response.status_code == 422


class TestPostGenerate:
    @pytest.mark.integration
    async def test_valid_yaml_returns_zip(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/generate",
            files={"file": ("intake.yaml", _renderable_intake_yaml(), "application/x-yaml")},
        )

        assert response.status_code == 200
        assert "application/zip" in response.headers["content-type"]
        zf = zipfile.ZipFile(BytesIO(response.content))
        assert zf.testzip() is None

    @pytest.mark.integration
    async def test_zip_contains_expected_files(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/generate",
            files={"file": ("intake.yaml", _renderable_intake_yaml(), "application/x-yaml")},
        )

        zf = zipfile.ZipFile(BytesIO(response.content))
        names = zf.namelist()
        assert any("CLAUDE.md" in n for n in names)
        assert any("docs/" in n for n in names)
        assert any("skills/" in n for n in names)

    @pytest.mark.integration
    async def test_invalid_yaml_returns_error(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/generate",
            files={"file": ("bad.yaml", b"invalid: yaml: [unterminated", "application/x-yaml")},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.integration
    async def test_no_file_returns_422(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/generate")

        assert response.status_code == 422

    @pytest.mark.integration
    async def test_content_disposition_has_filename(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/generate",
            files={"file": ("intake.yaml", _renderable_intake_yaml(), "application/x-yaml")},
        )

        assert response.status_code == 200
        disposition = response.headers.get("content-disposition", "")
        assert "attachment" in disposition
        assert ".zip" in disposition
