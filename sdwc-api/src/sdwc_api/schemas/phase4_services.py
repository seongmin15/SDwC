"""Phase 4 models: Services — all 5 types with Deployment and discriminated union."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from sdwc_api.schemas.enums import (
    AccessibilityLevel,
    ApiStyle,
    ApiVersioning,
    AttributeType,
    AuthMethod,
    BackendFramework,
    BackendLanguage,
    BuildTool,
    Cardinality,
    CdStrategy,
    CdTool,
    CiTool,
    CommunicationProtocol,
    ContainerRegistry,
    CssStrategy,
    DatabaseEngine,
    DatabaseRole,
    DataFormat,
    DeploymentTarget,
    DeviceFeatureType,
    DistributionChannel,
    EnvironmentName,
    ErrorResponseFormat,
    ExtractionMethod,
    FailureBehavior,
    FileStorageStrategy,
    GrpcStreaming,
    HttpMethod,
    IacTool,
    LoadMethod,
    LocalStorageType,
    MobileApproach,
    MobileFramework,
    NavigationPattern,
    OverlapPolicy,
    PaginationStyle,
    PartialFailureStrategy,
    PipelineFramework,
    PipelineLanguage,
    PipelineSchedule,
    PipelineType,
    PushServiceType,
    QualityCheckAction,
    RenderingStrategy,
    ResponsiveStrategy,
    SchemaChangeHandling,
    SecretsManagement,
    StateManagementLib,
    SyncAsync,
    TriggerType,
    UpdateStrategy,
    WebFramework,
    WebLanguage,
    WorkerFramework,
    WorkerLanguage,
)

# --- Shared service models ---


class FrameworkAlternative(BaseModel):
    """Rejected framework alternative."""

    name: str
    rejection_reason: str


class Library(BaseModel):
    """Key library dependency."""

    name: str
    purpose: str
    version_constraint: str | None = None


class ServiceCommunication(BaseModel):
    """Inter-service communication definition."""

    target: str
    protocol: CommunicationProtocol
    sync_async: SyncAsync


# --- Deployment (shared across all service types) ---


class DeploymentAlternative(BaseModel):
    """Rejected deployment target."""

    target: str
    rejection_reason: str


class Environment(BaseModel):
    """Deployment environment."""

    name: EnvironmentName
    purpose: str
    differences: str


class CiConfig(BaseModel):
    """CI configuration."""

    tool: CiTool
    pipeline_stages: str


class CdConfig(BaseModel):
    """CD configuration."""

    tool: CdTool
    strategy: CdStrategy


class IacConfig(BaseModel):
    """Infrastructure as Code configuration."""

    enabled: bool
    tool: IacTool | None = None


class Deployment(BaseModel):
    """Service deployment configuration."""

    target: DeploymentTarget
    target_rationale: str | None = None
    target_alternatives: list[DeploymentAlternative] | None = None
    environments: list[Environment] | None = None
    ci: CiConfig | None = None
    cd: CdConfig | None = None
    infrastructure_as_code: IacConfig | None = None
    container_registry: ContainerRegistry | None = None
    secrets_management: SecretsManagement | None = None


# --- Backend API service models ---


class DatabaseAlternative(BaseModel):
    """Rejected database alternative."""

    engine: str
    rejection_reason: str


class Database(BaseModel):
    """Database configuration."""

    engine: DatabaseEngine
    role: DatabaseRole
    rationale: str
    alternatives_considered: list[DatabaseAlternative] | None = None


class Attribute(BaseModel):
    """Entity attribute definition."""

    name: str
    type: AttributeType
    nullable: bool
    description: str


class Relationship(BaseModel):
    """Entity relationship."""

    target: str
    cardinality: Cardinality
    description: str


class Entity(BaseModel):
    """Data entity definition."""

    name: str
    description: str
    key_attributes: list[Attribute] = Field(min_length=1)
    relationships: list[Relationship] | None = None
    indexes: list[str] | None = None


class DataDecision(BaseModel):
    """Data storage design decision."""

    decision: str
    rationale: str
    tradeoff: str


class FileStorage(BaseModel):
    """File storage configuration."""

    strategy: FileStorageStrategy
    rationale: str
    size_limits: str
    retention_policy: str


class RateLimiting(BaseModel):
    """Rate limiting configuration."""

    enabled: bool
    strategy: str | None = None


class Auth(BaseModel):
    """Authentication configuration."""

    method: AuthMethod
    rationale: str | None = None
    if_none_risks_accepted: str | None = None


class RequestField(BaseModel):
    """API endpoint request field."""

    name: str
    type: str
    required: bool
    description: str


class ResponseField(BaseModel):
    """API endpoint response field."""

    name: str
    type: str
    required: bool
    description: str


class Endpoint(BaseModel):
    """REST API endpoint definition."""

    method: HttpMethod
    path: str
    description: str
    auth_required: bool = True
    idempotent: bool | None = None
    sync_async: SyncAsync | None = None
    request_fields: list[RequestField] | None = None
    response_fields: list[ResponseField] | None = None
    processing_steps: list[str] | None = None


class GraphQLOperation(BaseModel):
    """GraphQL query or mutation."""

    name: str
    arguments: str
    return_type: str
    description: str


class GraphQLSchema(BaseModel):
    """GraphQL schema definition."""

    schema_types: list[str]
    queries: list[GraphQLOperation]
    mutations: list[GraphQLOperation]


class GrpcService(BaseModel):
    """gRPC service definition."""

    name: str
    description: str


class RpcMethod(BaseModel):
    """gRPC RPC method definition."""

    service: str
    method: str
    request_type: str
    response_type: str
    streaming: GrpcStreaming | None = None
    description: str = ""


class GrpcDefinition(BaseModel):
    """gRPC service definitions."""

    services: list[GrpcService]
    rpc_methods: list[RpcMethod]


class BackendApiService(BaseModel):
    """Backend API service definition."""

    name: str
    type: Literal["backend_api"]
    responsibility: str
    communication_with: list[ServiceCommunication] | None = None
    language: BackendLanguage
    framework: BackendFramework
    framework_rationale: str | None = None
    framework_alternatives: list[FrameworkAlternative] | None = None
    build_tool: BuildTool
    build_tool_rationale: str | None = None
    key_libraries: list[Library] | None = None
    databases: list[Database] | None = None
    entities: list[Entity] | None = None
    data_storage_decisions: list[DataDecision] | None = None
    schema_evolution_strategy: str | None = None
    file_storage: FileStorage | None = None
    api_style: ApiStyle
    api_style_rationale: str | None = None
    api_versioning: ApiVersioning | None = None
    pagination: PaginationStyle | None = None
    rate_limiting: RateLimiting | None = None
    auth: Auth
    error_response_format: ErrorResponseFormat | None = None
    error_response_example: str | None = None
    endpoints: list[Endpoint] | None = None
    graphql: GraphQLSchema | None = None
    grpc: GrpcDefinition | None = None
    deployment: Deployment


# --- Web UI service models ---


class Component(BaseModel):
    """UI component definition."""

    name: str
    purpose: str


class Page(BaseModel):
    """Web page definition."""

    name: str
    purpose: str
    key_interactions: list[str] | None = None
    connected_endpoints: list[str] | None = None
    states: list[str] | None = None
    components: list[Component] | None = None


class PageTransition(BaseModel):
    """Page-to-page transition."""

    from_page: str = Field(alias="from")
    to: str
    condition: str


class WebUiService(BaseModel):
    """Web UI service definition."""

    name: str
    type: Literal["web_ui"]
    responsibility: str
    communication_with: list[ServiceCommunication] | None = None
    language: WebLanguage
    framework: WebFramework
    framework_rationale: str | None = None
    framework_alternatives: list[FrameworkAlternative] | None = None
    build_tool: BuildTool
    build_tool_rationale: str | None = None
    rendering_strategy: RenderingStrategy | None = None
    rendering_rationale: str | None = None
    css_strategy: CssStrategy | None = None
    state_management: StateManagementLib | None = None
    accessibility_level: AccessibilityLevel | None = None
    i18n_required: bool | None = None
    supported_languages: str | None = None
    responsive_strategy: ResponsiveStrategy | None = None
    browser_support: str | None = None
    offline_support: bool | None = None
    seo_requirements: str | None = None
    design_references: list[str] | None = None
    pages: list[Page] = Field(min_length=1)
    page_transitions: list[PageTransition] | None = None
    deployment: Deployment


# --- Worker service models ---


class WorkerInputField(BaseModel):
    """Worker input field."""

    name: str
    type: str
    description: str


class WorkerOutput(BaseModel):
    """Worker output result."""

    result: str
    description: str


class WorkerDependency(BaseModel):
    """Worker external dependency."""

    service: str
    failure_behavior: FailureBehavior


class Worker(BaseModel):
    """Worker task definition."""

    name: str
    responsibility: str
    trigger_type: TriggerType
    trigger_config: str
    processing_steps: list[str] | None = None
    input_fields: list[WorkerInputField] | None = None
    outputs: list[WorkerOutput] | None = None
    concurrency: int | None = None
    batch_size: int | None = None
    ordering_required: bool | None = None
    ordering_key: str | None = None
    overlap_policy: OverlapPolicy | None = None
    retry_policy: str | None = None
    timeout: str | None = None
    idempotent: bool
    idempotent_strategy: str | None = None
    failure_destination: str | None = None
    graceful_shutdown: str | None = None
    execution_logging: str | None = None
    dependencies: list[WorkerDependency] | None = None


class WorkerService(BaseModel):
    """Worker service definition."""

    name: str
    type: Literal["worker"]
    responsibility: str
    communication_with: list[ServiceCommunication] | None = None
    language: WorkerLanguage
    framework: WorkerFramework
    framework_rationale: str | None = None
    framework_alternatives: list[FrameworkAlternative] | None = None
    build_tool: BuildTool
    build_tool_rationale: str | None = None
    key_libraries: list[Library] | None = None
    workers: list[Worker] = Field(min_length=1)
    deployment: Deployment


# --- Mobile app service models ---


class Screen(BaseModel):
    """Mobile screen definition."""

    name: str
    purpose: str
    key_interactions: list[str]
    connected_endpoints: list[str]
    states: list[str]
    components: list[Component]


class ScreenTransition(BaseModel):
    """Screen-to-screen transition."""

    from_screen: str = Field(alias="from")
    to: str
    condition: str


class DeviceFeature(BaseModel):
    """Mobile device feature usage."""

    feature: DeviceFeatureType
    purpose: str
    permission: str
    denial_behavior: str


class NotificationType(BaseModel):
    """Push notification type."""

    type: str
    trigger: str
    content: str


class PushNotification(BaseModel):
    """Push notification configuration."""

    service: PushServiceType
    types: list[NotificationType]


class MobileAppService(BaseModel):
    """Mobile app service definition."""

    name: str
    type: Literal["mobile_app"]
    responsibility: str
    communication_with: list[ServiceCommunication] | None = None
    approach: MobileApproach
    framework: MobileFramework
    framework_rationale: str | None = None
    framework_alternatives: list[FrameworkAlternative] | None = None
    min_os_versions: str
    navigation_pattern: NavigationPattern | None = None
    screens: list[Screen] = Field(min_length=1)
    screen_transitions: list[ScreenTransition] | None = None
    offline_support: bool | None = None
    local_storage: LocalStorageType | None = None
    sync_strategy: str | None = None
    cache_policy: str | None = None
    device_features: list[DeviceFeature] | None = None
    push_notification: PushNotification | None = None
    distribution: DistributionChannel | None = None
    update_strategy: UpdateStrategy | None = None
    deep_link_scheme: str | None = None
    app_size_target: str | None = None
    deployment: Deployment


# --- Data pipeline service models ---


class Source(BaseModel):
    """Pipeline data source."""

    name: str
    system: str
    extraction_method: ExtractionMethod | None = None
    format: DataFormat | None = None


class Sink(BaseModel):
    """Pipeline data sink."""

    name: str
    system: str
    load_method: LoadMethod | None = None
    format: DataFormat | None = None


class QualityCheck(BaseModel):
    """Data quality check rule."""

    rule: str
    target: str
    on_failure: QualityCheckAction


class Pipeline(BaseModel):
    """Data pipeline definition."""

    name: str
    responsibility: str
    type: PipelineType
    sources: list[Source]
    transformation_steps: list[str] | None = None
    sinks: list[Sink]
    schedule: PipelineSchedule
    expected_duration: str | None = None
    volume_per_run: str | None = None
    quality_checks: list[QualityCheck] | None = None
    retry_policy: str | None = None
    partial_failure_strategy: PartialFailureStrategy | None = None
    recovery_strategy: str | None = None
    sla: str | None = None
    schema_change_handling: SchemaChangeHandling | None = None
    backfill_strategy: str | None = None
    depends_on: list[str] | None = None


class PipelineDependency(BaseModel):
    """Inter-pipeline dependency."""

    pipeline: str
    depends_on: str
    reason: str


class DataPipelineService(BaseModel):
    """Data pipeline service definition."""

    name: str
    type: Literal["data_pipeline"]
    responsibility: str
    communication_with: list[ServiceCommunication] | None = None
    language: PipelineLanguage
    framework: PipelineFramework
    framework_rationale: str | None = None
    framework_alternatives: list[FrameworkAlternative] | None = None
    build_tool: BuildTool
    build_tool_rationale: str | None = None
    key_libraries: list[Library] | None = None
    pipelines: list[Pipeline] = Field(min_length=1)
    pipeline_dependencies: list[PipelineDependency] | None = None
    deployment: Deployment


# --- Discriminated union ---

Service = Annotated[
    BackendApiService | WebUiService | WorkerService | MobileAppService | DataPipelineService,
    Field(discriminator="type"),
]
