"""Tests for Phase 4 models: Services (all 5 types) and discriminated union."""

from typing import Annotated

import pytest
from pydantic import BaseModel, Field, ValidationError

from sdwc_api.schemas.phase4_services import (
    Auth,
    BackendApiService,
    Component,
    DataPipelineService,
    Deployment,
    Endpoint,
    Entity,
    Attribute,
    MobileAppService,
    Page,
    Pipeline,
    Screen,
    Service,
    Sink,
    Source,
    WebUiService,
    Worker,
    WorkerService,
)


# --- Helper: minimal Deployment ---


def _deployment(**overrides: object) -> Deployment:
    defaults: dict[str, object] = {"target": "docker_compose"}
    defaults.update(overrides)
    return Deployment(**defaults)  # type: ignore[arg-type]


# --- BackendApiService ---


class TestBackendApiService:
    def test_create_with_required_fields_succeeds(self) -> None:
        svc = BackendApiService(
            name="my-api",
            type="backend_api",
            responsibility="Handle API requests",
            language="python",
            framework="fastapi",
            build_tool="poetry",
            api_style="rest",
            auth=Auth(method="none", if_none_risks_accepted="Public utility"),
            deployment=_deployment(),
        )
        assert svc.type == "backend_api"
        assert svc.databases is None
        assert svc.endpoints is None

    def test_create_with_endpoints_succeeds(self) -> None:
        svc = BackendApiService(
            name="my-api",
            type="backend_api",
            responsibility="x",
            language="typescript",
            framework="express",
            build_tool="npm",
            api_style="rest",
            auth=Auth(method="jwt"),
            endpoints=[
                Endpoint(method="GET", path="/users", description="List users"),
                Endpoint(method="POST", path="/users", description="Create user"),
            ],
            deployment=_deployment(),
        )
        assert len(svc.endpoints) == 2

    def test_create_with_entities_succeeds(self) -> None:
        svc = BackendApiService(
            name="my-api",
            type="backend_api",
            responsibility="x",
            language="java",
            framework="spring",
            build_tool="gradle",
            api_style="rest",
            auth=Auth(method="session"),
            entities=[
                Entity(
                    name="User",
                    description="App user",
                    key_attributes=[
                        Attribute(name="id", type="uuid", nullable=False, description="PK"),
                        Attribute(name="email", type="string", nullable=False, description="Email"),
                    ],
                ),
            ],
            deployment=_deployment(),
        )
        assert len(svc.entities[0].key_attributes) == 2

    def test_invalid_api_style_raises_error(self) -> None:
        """CRITICAL: api_style enum must reject invalid values."""
        with pytest.raises(ValidationError) as exc_info:
            BackendApiService(
                name="x",
                type="backend_api",
                responsibility="x",
                language="python",
                framework="fastapi",
                build_tool="poetry",
                api_style="soap",
                auth=Auth(method="none"),
                deployment=_deployment(),
            )
        assert "api_style" in str(exc_info.value)

    def test_invalid_backend_language_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            BackendApiService(
                name="x",
                type="backend_api",
                responsibility="x",
                language="php",
                framework="fastapi",
                build_tool="poetry",
                api_style="rest",
                auth=Auth(method="none"),
                deployment=_deployment(),
            )
        assert "language" in str(exc_info.value)

    def test_invalid_auth_method_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Auth(method="basic")
        assert "method" in str(exc_info.value)

    def test_empty_entity_attributes_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Entity(name="x", description="x", key_attributes=[])
        assert "key_attributes" in str(exc_info.value)


# --- WebUiService ---


class TestWebUiService:
    def test_create_with_required_fields_succeeds(self) -> None:
        svc = WebUiService(
            name="my-web",
            type="web_ui",
            responsibility="User interface",
            language="typescript",
            framework="react",
            build_tool="vite",
            pages=[Page(name="Home", purpose="Main page")],
            deployment=_deployment(target="vercel"),
        )
        assert svc.type == "web_ui"
        assert svc.css_strategy is None

    def test_create_with_all_optional_fields_succeeds(self) -> None:
        svc = WebUiService(
            name="my-web",
            type="web_ui",
            responsibility="x",
            language="typescript",
            framework="next",
            build_tool="pnpm",
            rendering_strategy="ssr",
            css_strategy="tailwind",
            state_management="zustand",
            accessibility_level="wcag_aa",
            responsive_strategy="mobile_first",
            pages=[
                Page(
                    name="Home",
                    purpose="Landing",
                    components=[Component(name="Hero", purpose="Banner")],
                ),
            ],
            deployment=_deployment(),
        )
        assert svc.rendering_strategy == "ssr"
        assert svc.state_management == "zustand"

    def test_empty_pages_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            WebUiService(
                name="x",
                type="web_ui",
                responsibility="x",
                language="typescript",
                framework="react",
                build_tool="vite",
                pages=[],
                deployment=_deployment(),
            )
        assert "pages" in str(exc_info.value)

    def test_invalid_web_language_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            WebUiService(
                name="x",
                type="web_ui",
                responsibility="x",
                language="python",
                framework="react",
                build_tool="vite",
                pages=[Page(name="x", purpose="x")],
                deployment=_deployment(),
            )
        assert "language" in str(exc_info.value)


# --- WorkerService ---


class TestWorkerService:
    def test_create_with_required_fields_succeeds(self) -> None:
        svc = WorkerService(
            name="my-worker",
            type="worker",
            responsibility="Process jobs",
            language="python",
            framework="celery",
            build_tool="poetry",
            workers=[
                Worker(
                    name="email-sender",
                    responsibility="Send emails",
                    trigger_type="queue",
                    trigger_config="email_queue",
                    idempotent=True,
                ),
            ],
            deployment=_deployment(),
        )
        assert svc.type == "worker"

    def test_invalid_trigger_type_raises_error(self) -> None:
        """CRITICAL: trigger_type enum must reject invalid values."""
        with pytest.raises(ValidationError) as exc_info:
            Worker(
                name="x",
                responsibility="x",
                trigger_type="manual",
                trigger_config="x",
                idempotent=True,
            )
        assert "trigger_type" in str(exc_info.value)

    def test_empty_workers_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            WorkerService(
                name="x",
                type="worker",
                responsibility="x",
                language="python",
                framework="celery",
                build_tool="poetry",
                workers=[],
                deployment=_deployment(),
            )
        assert "workers" in str(exc_info.value)

    def test_worker_with_cron_overlap_policy_succeeds(self) -> None:
        w = Worker(
            name="daily-report",
            responsibility="Generate reports",
            trigger_type="cron",
            trigger_config="0 0 * * *",
            idempotent=False,
            overlap_policy="skip",
        )
        assert w.overlap_policy == "skip"


# --- MobileAppService ---


class TestMobileAppService:
    def test_create_with_required_fields_succeeds(self) -> None:
        svc = MobileAppService(
            name="my-app",
            type="mobile_app",
            responsibility="Mobile client",
            approach="cross_platform",
            framework="react_native",
            min_os_versions="iOS 15, Android 12",
            screens=[
                Screen(
                    name="Home",
                    purpose="Main",
                    key_interactions=["Tap"],
                    connected_endpoints=["/api/home"],
                    states=["loading", "ready"],
                    components=[Component(name="Feed", purpose="Content")],
                ),
            ],
            deployment=_deployment(),
        )
        assert svc.type == "mobile_app"
        assert svc.approach == "cross_platform"

    def test_empty_screens_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            MobileAppService(
                name="x",
                type="mobile_app",
                responsibility="x",
                approach="native",
                framework="swift",
                min_os_versions="iOS 16",
                screens=[],
                deployment=_deployment(),
            )
        assert "screens" in str(exc_info.value)

    def test_invalid_mobile_approach_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            MobileAppService(
                name="x",
                type="mobile_app",
                responsibility="x",
                approach="web_wrapper",
                framework="flutter",
                min_os_versions="x",
                screens=[
                    Screen(
                        name="x",
                        purpose="x",
                        key_interactions=["x"],
                        connected_endpoints=["x"],
                        states=["x"],
                        components=[Component(name="x", purpose="x")],
                    ),
                ],
                deployment=_deployment(),
            )
        assert "approach" in str(exc_info.value)


# --- DataPipelineService ---


class TestDataPipelineService:
    def test_create_with_required_fields_succeeds(self) -> None:
        svc = DataPipelineService(
            name="my-pipeline",
            type="data_pipeline",
            responsibility="ETL",
            language="python",
            framework="airflow",
            build_tool="poetry",
            pipelines=[
                Pipeline(
                    name="daily-etl",
                    responsibility="Extract and load",
                    type="batch",
                    sources=[Source(name="db", system="postgresql")],
                    sinks=[Sink(name="warehouse", system="bigquery")],
                    schedule="cron",
                ),
            ],
            deployment=_deployment(),
        )
        assert svc.type == "data_pipeline"

    def test_empty_pipelines_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            DataPipelineService(
                name="x",
                type="data_pipeline",
                responsibility="x",
                language="python",
                framework="dagster",
                build_tool="poetry",
                pipelines=[],
                deployment=_deployment(),
            )
        assert "pipelines" in str(exc_info.value)

    def test_invalid_pipeline_type_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Pipeline(
                name="x",
                responsibility="x",
                type="realtime",
                sources=[Source(name="x", system="x")],
                sinks=[Sink(name="x", system="x")],
                schedule="cron",
            )
        assert "type" in str(exc_info.value)


# --- Discriminated union ---


class _ServiceWrapper(BaseModel):
    """Wrapper to test discriminated union parsing."""

    service: Service


class TestServiceDiscriminatedUnion:
    def test_backend_api_resolved_by_type(self) -> None:
        data = {
            "service": {
                "name": "api",
                "type": "backend_api",
                "responsibility": "x",
                "language": "python",
                "framework": "fastapi",
                "build_tool": "poetry",
                "api_style": "rest",
                "auth": {"method": "none"},
                "deployment": {"target": "docker_compose"},
            },
        }
        w = _ServiceWrapper.model_validate(data)
        assert isinstance(w.service, BackendApiService)

    def test_web_ui_resolved_by_type(self) -> None:
        data = {
            "service": {
                "name": "web",
                "type": "web_ui",
                "responsibility": "x",
                "language": "typescript",
                "framework": "react",
                "build_tool": "vite",
                "pages": [{"name": "Home", "purpose": "Main"}],
                "deployment": {"target": "vercel"},
            },
        }
        w = _ServiceWrapper.model_validate(data)
        assert isinstance(w.service, WebUiService)

    def test_worker_resolved_by_type(self) -> None:
        data = {
            "service": {
                "name": "worker",
                "type": "worker",
                "responsibility": "x",
                "language": "python",
                "framework": "celery",
                "build_tool": "poetry",
                "workers": [
                    {
                        "name": "w",
                        "responsibility": "x",
                        "trigger_type": "queue",
                        "trigger_config": "q",
                        "idempotent": True,
                    },
                ],
                "deployment": {"target": "kubernetes"},
            },
        }
        w = _ServiceWrapper.model_validate(data)
        assert isinstance(w.service, WorkerService)

    def test_mobile_app_resolved_by_type(self) -> None:
        data = {
            "service": {
                "name": "app",
                "type": "mobile_app",
                "responsibility": "x",
                "approach": "cross_platform",
                "framework": "flutter",
                "min_os_versions": "iOS 15",
                "screens": [
                    {
                        "name": "Home",
                        "purpose": "x",
                        "key_interactions": ["tap"],
                        "connected_endpoints": ["/api"],
                        "states": ["idle"],
                        "components": [{"name": "c", "purpose": "x"}],
                    },
                ],
                "deployment": {"target": "bare_metal"},
            },
        }
        w = _ServiceWrapper.model_validate(data)
        assert isinstance(w.service, MobileAppService)

    def test_data_pipeline_resolved_by_type(self) -> None:
        data = {
            "service": {
                "name": "etl",
                "type": "data_pipeline",
                "responsibility": "x",
                "language": "python",
                "framework": "airflow",
                "build_tool": "poetry",
                "pipelines": [
                    {
                        "name": "p",
                        "responsibility": "x",
                        "type": "batch",
                        "sources": [{"name": "s", "system": "pg"}],
                        "sinks": [{"name": "k", "system": "bq"}],
                        "schedule": "cron",
                    },
                ],
                "deployment": {"target": "kubernetes"},
            },
        }
        w = _ServiceWrapper.model_validate(data)
        assert isinstance(w.service, DataPipelineService)

    def test_invalid_type_raises_error(self) -> None:
        data = {
            "service": {
                "name": "x",
                "type": "serverless_function",
                "responsibility": "x",
            },
        }
        with pytest.raises(ValidationError) as exc_info:
            _ServiceWrapper.model_validate(data)
        assert "type" in str(exc_info.value)
