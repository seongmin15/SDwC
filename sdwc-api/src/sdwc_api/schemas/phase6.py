"""Phase 6 models: Performance, Availability, Observability, External Systems (HOW-WELL)."""

from pydantic import BaseModel

from sdwc_api.schemas.enums import (
    Likelihood,
    LongRunningHandling,
    ProgressFeedback,
)

# --- Performance ---


class ResponseTimeTarget(BaseModel):
    """Response time target for a specific endpoint or flow."""

    endpoint_or_flow: str
    p50_target: str
    p99_target: str


class DataVolume(BaseModel):
    """Expected data volume and growth."""

    initial: str
    one_year: str
    growth_rate: str


class LongRunningOperation(BaseModel):
    """Long-running operation configuration."""

    operation: str
    expected_duration: str
    handling: LongRunningHandling
    timeout_policy: str
    progress_feedback: ProgressFeedback


class Performance(BaseModel):
    """Performance requirements and targets."""

    expected_concurrent_users: str
    response_time_targets: list[ResponseTimeTarget] | None = None
    throughput_target: str | None = None
    data_volume: DataVolume | None = None
    caching_strategy: str | None = None
    long_running_operations: list[LongRunningOperation] | None = None


# --- Availability ---


class DisasterRecovery(BaseModel):
    """Disaster recovery configuration."""

    rpo: str
    rto: str
    backup_strategy: str


class Availability(BaseModel):
    """Availability requirements."""

    target: str | None = None
    acceptable_downtime: str | None = None
    disaster_recovery: DisasterRecovery | None = None
    single_points_of_failure: list[str] | None = None


# --- Observability ---


class Logging(BaseModel):
    """Logging configuration."""

    framework: str
    structured: bool
    sensitive_data_masking: bool
    retention_period: str


class Metrics(BaseModel):
    """Metrics collection configuration."""

    tool: str
    key_metrics: list[str]
    dashboards: str


class Alerting(BaseModel):
    """Alerting configuration."""

    tool: str
    critical_alerts: list[str]


class Observability(BaseModel):
    """Observability configuration."""

    logging: Logging | None = None
    metrics: Metrics | None = None
    alerting: Alerting | None = None


# --- External Systems ---


class ExternalSystem(BaseModel):
    """External system integration."""

    name: str
    purpose: str
    protocol: str
    reliability: Likelihood | None = None
    fallback: str | None = None
