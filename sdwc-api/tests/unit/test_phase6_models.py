"""Tests for Phase 6 models: Performance, Availability, Observability, External Systems."""

import pytest
from pydantic import ValidationError

from sdwc_api.schemas.phase6 import (
    Alerting,
    Availability,
    DataVolume,
    DisasterRecovery,
    ExternalSystem,
    HealthCheck,
    Logging,
    LongRunningOperation,
    Metrics,
    Observability,
    Performance,
    ResponseTimeTarget,
    Scalability,
    Tracing,
)

# --- Performance ---


class TestPerformance:
    def test_create_with_required_fields_succeeds(self) -> None:
        p = Performance(expected_concurrent_users="100")
        assert p.expected_concurrent_users == "100"
        assert p.response_time_targets is None
        assert p.throughput_target is None
        assert p.data_volume is None
        assert p.caching_strategy is None
        assert p.long_running_operations is None

    def test_create_with_all_fields_succeeds(self) -> None:
        p = Performance(
            expected_concurrent_users="50",
            response_time_targets=[
                ResponseTimeTarget(
                    endpoint_or_flow="POST /generate",
                    p50_target="2s",
                    p99_target="10s",
                ),
            ],
            throughput_target="100 req/s",
            data_volume=DataVolume(initial="10GB", one_year="50GB", growth_rate="5x"),
            caching_strategy="LRU for templates",
            long_running_operations=[
                LongRunningOperation(
                    operation="ZIP generation",
                    expected_duration="5s",
                    handling="background",
                    timeout_policy="30s hard limit",
                    progress_feedback="polling",
                ),
            ],
        )
        assert len(p.response_time_targets) == 1
        assert p.data_volume is not None
        assert len(p.long_running_operations) == 1

    def test_invalid_handling_enum_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            LongRunningOperation(
                operation="x",
                expected_duration="1s",
                handling="sync",  # type: ignore[arg-type]
                timeout_policy="x",
                progress_feedback="polling",
            )
        assert "handling" in str(exc_info.value)

    def test_invalid_progress_feedback_enum_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            LongRunningOperation(
                operation="x",
                expected_duration="1s",
                handling="background",
                timeout_policy="x",
                progress_feedback="push",  # type: ignore[arg-type]
            )
        assert "progress_feedback" in str(exc_info.value)


# --- Availability ---


class TestAvailability:
    def test_create_with_all_optional_defaults(self) -> None:
        a = Availability()
        assert a.target is None
        assert a.acceptable_downtime is None
        assert a.disaster_recovery is None
        assert a.single_points_of_failure is None

    def test_create_with_all_fields_succeeds(self) -> None:
        a = Availability(
            target="99.9%",
            acceptable_downtime="< 10min/month",
            disaster_recovery=DisasterRecovery(
                rpo="1 hour",
                rto="4 hours",
                backup_strategy="Daily snapshots",
            ),
            single_points_of_failure=["Single DB instance"],
        )
        assert a.disaster_recovery is not None
        assert a.disaster_recovery.rpo == "1 hour"


# --- Observability ---


class TestTracing:
    def test_create_with_defaults(self) -> None:
        t = Tracing()
        assert t.enabled is False
        assert t.tool is None

    def test_create_with_all_fields(self) -> None:
        t = Tracing(enabled=True, tool="jaeger")
        assert t.enabled is True
        assert t.tool == "jaeger"


class TestHealthCheck:
    def test_create_with_required_fields(self) -> None:
        hc = HealthCheck(endpoint="/health", checks="db,redis")
        assert hc.endpoint == "/health"
        assert hc.checks == "db,redis"

    def test_missing_required_fields_raises_error(self) -> None:
        with pytest.raises(ValidationError):
            HealthCheck()  # type: ignore[call-arg]


class TestObservability:
    def test_create_with_all_optional_defaults(self) -> None:
        o = Observability()
        assert o.logging is None
        assert o.metrics is None
        assert o.alerting is None
        assert o.tracing is None
        assert o.health_checks is None

    def test_create_with_all_fields_succeeds(self) -> None:
        o = Observability(
            logging=Logging(
                framework="structlog",
                structured=True,
                sensitive_data_masking=True,
                retention_period="30 days",
            ),
            metrics=Metrics(
                tool="prometheus",
                key_metrics=["request_count", "latency_p99"],
                dashboards="Grafana",
            ),
            alerting=Alerting(
                tool="pagerduty",
                critical_alerts=["error_rate > 5%", "latency_p99 > 10s"],
            ),
            tracing=Tracing(enabled=True, tool="jaeger"),
            health_checks=[HealthCheck(endpoint="/health", checks="db,redis")],
        )
        assert o.logging is not None
        assert o.logging.structured is True
        assert len(o.metrics.key_metrics) == 2
        assert o.tracing.enabled is True
        assert len(o.health_checks) == 1


class TestLoggingDefaults:
    def test_structured_defaults_to_false(self) -> None:
        log = Logging(framework="structlog", retention_period="30d")
        assert log.structured is False
        assert log.sensitive_data_masking is False

    def test_explicit_values_override_defaults(self) -> None:
        log = Logging(framework="structlog", structured=True, sensitive_data_masking=True, retention_period="30d")
        assert log.structured is True
        assert log.sensitive_data_masking is True


class TestScalability:
    def test_create_with_all_optional_defaults(self) -> None:
        s = Scalability()
        assert s.strategy is None
        assert s.bottlenecks is None
        assert s.scaling_trigger is None

    def test_create_with_all_fields(self) -> None:
        s = Scalability(strategy="horizontal", bottlenecks="DB connections", scaling_trigger="CPU > 80%")
        assert s.strategy == "horizontal"

    def test_invalid_strategy_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Scalability(strategy="diagonal")  # type: ignore[arg-type]
        assert "strategy" in str(exc_info.value)

    def test_all_valid_strategy_values(self) -> None:
        for v in ("vertical", "horizontal", "auto"):
            s = Scalability(strategy=v)
            assert s.strategy == v


# --- ExternalSystem ---


class TestExternalSystem:
    def test_create_with_required_fields_succeeds(self) -> None:
        es = ExternalSystem(name="GitHub API", purpose="Fetch repos", protocol="https")
        assert es.reliability is None
        assert es.fallback is None

    def test_create_with_all_fields_succeeds(self) -> None:
        es = ExternalSystem(
            name="GitHub API",
            purpose="Fetch repos",
            protocol="https",
            reliability="high",
            fallback="Use cached data",
        )
        assert es.reliability == "high"

    def test_invalid_reliability_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ExternalSystem(
                name="x",
                purpose="x",
                protocol="x",
                reliability="very_high",  # type: ignore[arg-type]
            )
        assert "reliability" in str(exc_info.value)
