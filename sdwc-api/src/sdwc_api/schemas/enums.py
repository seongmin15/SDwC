"""Shared enum definitions for intake YAML validation."""

from enum import StrEnum

# Phase 1 enums


class Severity(StrEnum):
    """Problem severity level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Frequency(StrEnum):
    """Problem occurrence frequency."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    OCCASIONAL = "occasional"


# Phase 2 enums


class GoalPriority(StrEnum):
    """Goal priority level."""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class ScopePriority(StrEnum):
    """Feature scope priority (MoSCoW)."""

    MUST = "must"
    SHOULD = "should"
    COULD = "could"


class ComplexityEstimate(StrEnum):
    """Feature complexity T-shirt size."""

    S = "S"
    M = "M"
    L = "L"
    XL = "XL"


class PlannedPhase(StrEnum):
    """Planned implementation phase for out-of-scope features."""

    V2 = "v2"
    V3 = "v3"
    POST_LAUNCH = "post_launch"
    BACKLOG = "backlog"


class ConstraintSource(StrEnum):
    """Source of a project constraint."""

    TECHNICAL = "technical"
    BUSINESS = "business"
    LEGAL = "legal"
    REGULATORY = "regulatory"


class Negotiable(StrEnum):
    """Whether a constraint is negotiable."""

    YES = "yes"
    NO = "no"
    PARTIALLY = "partially"


class TimelineFlexibility(StrEnum):
    """Deadline flexibility level."""

    RIGID = "rigid"
    FLEXIBLE = "flexible"
    ASPIRATIONAL = "aspirational"


# Phase 3 enums


class TechProficiency(StrEnum):
    """User technical proficiency level."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class UsageFrequency(StrEnum):
    """Expected usage frequency."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class InfluenceLevel(StrEnum):
    """Stakeholder influence level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CollaborationMode(StrEnum):
    """AI collaboration mode per service.

    CRITICAL: This enum controls how Claude interacts with the codebase.
    - autonomous: Claude writes code, human reviews.
    - collaborative: Claude and human share responsibilities.
    - learning: Claude only plans/explains, human codes.
    """

    AUTONOMOUS = "autonomous"
    COLLABORATIVE = "collaborative"
    LEARNING = "learning"


class TestCaseCoverage(StrEnum):
    """Test coverage level per service."""

    BASIC = "basic"
    STANDARD = "standard"
    THOROUGH = "thorough"


# Phase 4 enums — Architecture


class ArchitecturePattern(StrEnum):
    """System architecture pattern."""

    MONOLITH = "monolith"
    MICROSERVICES = "microservices"
    MODULAR_MONOLITH = "modular_monolith"


class InternalStyle(StrEnum):
    """Internal architecture style."""

    HEXAGONAL = "hexagonal"
    CLEAN = "clean"
    LAYERED = "layered"
    NONE = "none"


# Phase 4 enums — Services common


class ServiceType(StrEnum):
    """Service type identifier."""

    BACKEND_API = "backend_api"
    WEB_UI = "web_ui"
    WORKER = "worker"
    MOBILE_APP = "mobile_app"
    DATA_PIPELINE = "data_pipeline"


class CommunicationProtocol(StrEnum):
    """Inter-service communication protocol."""

    HTTP = "http"
    GRPC = "grpc"
    AMQP = "amqp"
    KAFKA = "kafka"
    WEBSOCKET = "websocket"


class SyncAsync(StrEnum):
    """Synchronous or asynchronous communication."""

    SYNC = "sync"
    ASYNC = "async"


class BuildTool(StrEnum):
    """Project build tool."""

    POETRY = "poetry"
    PIP = "pip"
    NPM = "npm"
    PNPM = "pnpm"
    YARN = "yarn"
    GRADLE = "gradle"
    MAVEN = "maven"
    CARGO = "cargo"
    GO_MOD = "go_mod"
    VITE = "vite"
    WEBPACK = "webpack"
    TURBOPACK = "turbopack"
    BUNDLER = "bundler"
    SBT = "sbt"


# Phase 4 enums — Backend-specific


class BackendLanguage(StrEnum):
    """Backend API programming language."""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    CSHARP = "csharp"
    KOTLIN = "kotlin"


class BackendFramework(StrEnum):
    """Backend API framework."""

    FASTAPI = "fastapi"
    DJANGO = "django"
    EXPRESS = "express"
    NESTJS = "nestjs"
    SPRING = "spring"
    GIN = "gin"
    ACTIX = "actix"
    RAILS = "rails"
    ASPNET = "aspnet"


class DatabaseEngine(StrEnum):
    """Database engine."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    SQLITE = "sqlite"
    DYNAMODB = "dynamodb"
    ELASTICSEARCH = "elasticsearch"
    NEO4J = "neo4j"


class DatabaseRole(StrEnum):
    """Database role in the system."""

    PRIMARY = "primary"
    CACHE = "cache"
    SEARCH = "search"
    QUEUE = "queue"
    ANALYTICS = "analytics"
    SESSION = "session"


class AttributeType(StrEnum):
    """Entity attribute data type."""

    STRING = "string"
    INTEGER = "integer"
    UUID = "uuid"
    TIMESTAMP = "timestamp"
    BOOLEAN = "boolean"
    FLOAT = "float"
    TEXT = "text"
    JSON = "json"
    ENUM = "enum"
    DATE = "date"


class Cardinality(StrEnum):
    """Entity relationship cardinality."""

    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:N"
    MANY_TO_MANY = "N:M"


class FileStorageStrategy(StrEnum):
    """File storage strategy."""

    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"
    AZURE_BLOB = "azure_blob"
    MINIO = "minio"


class ApiStyle(StrEnum):
    """API style.

    CRITICAL: Controls template branching for endpoint rendering.
    """

    REST = "rest"
    GRAPHQL = "graphql"
    GRPC = "grpc"


class ApiVersioning(StrEnum):
    """API versioning strategy."""

    URL_PREFIX = "url_prefix"
    HEADER = "header"
    QUERY_PARAM = "query_param"
    NONE = "none"


class PaginationStyle(StrEnum):
    """API pagination style."""

    CURSOR = "cursor"
    OFFSET = "offset"
    NONE = "none"


class AuthMethod(StrEnum):
    """Authentication method."""

    JWT = "jwt"
    SESSION = "session"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    NONE = "none"


class ErrorResponseFormat(StrEnum):
    """Error response format."""

    RFC7807 = "rfc7807"
    CUSTOM = "custom"
    GRAPHQL_ERRORS = "graphql_errors"


class HttpMethod(StrEnum):
    """HTTP request method."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class GrpcStreaming(StrEnum):
    """gRPC streaming mode."""

    NONE = "none"
    SERVER = "server"
    CLIENT = "client"
    BIDIRECTIONAL = "bidirectional"


# Phase 4 enums — Web-specific


class WebLanguage(StrEnum):
    """Web UI programming language."""

    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"


class WebFramework(StrEnum):
    """Web UI framework."""

    REACT = "react"
    VUE = "vue"
    SVELTE = "svelte"
    NEXT = "next"
    NUXT = "nuxt"
    ANGULAR = "angular"
    SOLID = "solid"
    ASTRO = "astro"


class RenderingStrategy(StrEnum):
    """Web rendering strategy."""

    SPA = "spa"
    SSR = "ssr"
    SSG = "ssg"
    ISR = "isr"


class CssStrategy(StrEnum):
    """CSS strategy."""

    TAILWIND = "tailwind"
    CSS_MODULES = "css_modules"
    STYLED_COMPONENTS = "styled_components"
    SASS = "sass"
    VANILLA_CSS = "vanilla_css"
    EMOTION = "emotion"


class StateManagementLib(StrEnum):
    """State management library."""

    ZUSTAND = "zustand"
    REDUX = "redux"
    RECOIL = "recoil"
    JOTAI = "jotai"
    CONTEXT = "context"
    PINIA = "pinia"
    MOBX = "mobx"


class AccessibilityLevel(StrEnum):
    """Accessibility compliance level."""

    WCAG_AA = "wcag_aa"
    WCAG_AAA = "wcag_aaa"
    BASIC = "basic"
    NONE = "none"


class ResponsiveStrategy(StrEnum):
    """Responsive design strategy."""

    MOBILE_FIRST = "mobile_first"
    DESKTOP_FIRST = "desktop_first"


# Phase 4 enums — Worker-specific


class WorkerLanguage(StrEnum):
    """Worker programming language."""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    KOTLIN = "kotlin"
    RUBY = "ruby"
    GO = "go"


class WorkerFramework(StrEnum):
    """Worker framework."""

    CELERY = "celery"
    BULLMQ = "bullmq"
    SIDEKIQ = "sidekiq"
    SPRING_BATCH = "spring_batch"
    TEMPORAL = "temporal"


class TriggerType(StrEnum):
    """Worker trigger type.

    CRITICAL: Controls template branching for worker configuration.
    """

    QUEUE = "queue"
    CRON = "cron"
    EVENT = "event"
    WEBHOOK = "webhook"


class OverlapPolicy(StrEnum):
    """Cron worker overlap policy."""

    SKIP = "skip"
    QUEUE = "queue"
    PARALLEL = "parallel"


class FailureBehavior(StrEnum):
    """Worker dependency failure behavior."""

    RETRY = "retry"
    SKIP = "skip"
    FAIL = "fail"


# Phase 4 enums — Mobile-specific


class MobileApproach(StrEnum):
    """Mobile development approach."""

    NATIVE = "native"
    CROSS_PLATFORM = "cross_platform"
    HYBRID = "hybrid"


class MobileFramework(StrEnum):
    """Mobile framework."""

    REACT_NATIVE = "react_native"
    FLUTTER = "flutter"
    SWIFT = "swift"
    KOTLIN_MOBILE = "kotlin_mobile"
    SWIFTUI = "swiftui"
    JETPACK_COMPOSE = "jetpack_compose"


class NavigationPattern(StrEnum):
    """Mobile navigation pattern."""

    TAB = "tab"
    DRAWER = "drawer"
    STACK = "stack"
    BOTTOM_NAV = "bottom_nav"


class LocalStorageType(StrEnum):
    """Mobile local storage type."""

    SQLITE = "sqlite"
    REALM = "realm"
    ASYNC_STORAGE = "async_storage"
    MMKV = "mmkv"
    CORE_DATA = "core_data"


class DeviceFeatureType(StrEnum):
    """Mobile device feature."""

    CAMERA = "camera"
    GPS = "gps"
    BIOMETRICS = "biometrics"
    PUSH = "push"
    NFC = "nfc"
    BLUETOOTH = "bluetooth"
    ACCELEROMETER = "accelerometer"
    CONTACTS = "contacts"


class PushServiceType(StrEnum):
    """Push notification service."""

    FCM = "fcm"
    APNS = "apns"
    ONESIGNAL = "onesignal"
    EXPO_PUSH = "expo_push"


class DistributionChannel(StrEnum):
    """App distribution channel."""

    APP_STORE = "app_store"
    PLAY_STORE = "play_store"
    ENTERPRISE = "enterprise"
    BOTH_STORES = "both_stores"
    TESTFLIGHT = "testflight"


class UpdateStrategy(StrEnum):
    """App update strategy."""

    FORCE = "force"
    SOFT = "soft"
    IN_APP = "in_app"
    CODE_PUSH = "code_push"


# Phase 4 enums — Pipeline-specific


class PipelineLanguage(StrEnum):
    """Data pipeline programming language."""

    PYTHON = "python"
    JAVA = "java"
    SCALA = "scala"
    SQL = "sql"


class PipelineFramework(StrEnum):
    """Data pipeline framework."""

    AIRFLOW = "airflow"
    DAGSTER = "dagster"
    PREFECT = "prefect"
    SPARK = "spark"
    DBT = "dbt"
    FLINK = "flink"


class PipelineType(StrEnum):
    """Data pipeline type."""

    BATCH = "batch"
    STREAMING = "streaming"
    MICRO_BATCH = "micro_batch"
    HYBRID = "hybrid"


class ExtractionMethod(StrEnum):
    """Data extraction method."""

    FULL = "full"
    INCREMENTAL = "incremental"
    CDC = "cdc"
    API_POLL = "api_poll"


class DataFormat(StrEnum):
    """Data serialization format."""

    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    XML = "xml"


class LoadMethod(StrEnum):
    """Data load method."""

    UPSERT = "upsert"
    APPEND = "append"
    OVERWRITE = "overwrite"
    MERGE = "merge"


class PipelineSchedule(StrEnum):
    """Pipeline execution schedule."""

    CRON = "cron"
    REAL_TIME = "real_time"
    TRIGGER_BASED = "trigger_based"


class QualityCheckAction(StrEnum):
    """Action on data quality check failure."""

    ABORT = "abort"
    WARN = "warn"
    QUARANTINE = "quarantine"


class PartialFailureStrategy(StrEnum):
    """Strategy for partial pipeline failures."""

    SKIP_BAD = "skip_bad"
    FAIL_ALL = "fail_all"
    DEAD_LETTER = "dead_letter"


class SchemaChangeHandling(StrEnum):
    """Schema change handling strategy."""

    AUTO_DETECT = "auto_detect"
    FAIL = "fail"
    ALERT = "alert"


# Phase 4 enums — Deployment


class DeploymentTarget(StrEnum):
    """Deployment target platform."""

    DOCKER_COMPOSE = "docker_compose"
    KUBERNETES = "kubernetes"
    ECS = "ecs"
    LAMBDA = "lambda"
    CLOUD_RUN = "cloud_run"
    FLY_IO = "fly_io"
    RAILWAY = "railway"
    VERCEL = "vercel"
    BARE_METAL = "bare_metal"


class EnvironmentName(StrEnum):
    """Deployment environment name."""

    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"


class CiTool(StrEnum):
    """CI tool."""

    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    CIRCLECI = "circleci"
    BITBUCKET_PIPELINES = "bitbucket_pipelines"


class CdTool(StrEnum):
    """CD tool."""

    ARGOCD = "argocd"
    FLUXCD = "fluxcd"
    SPINNAKER = "spinnaker"
    NONE = "none"


class CdStrategy(StrEnum):
    """CD deployment strategy."""

    GITOPS = "gitops"
    PUSH = "push"
    MANUAL = "manual"


class IacTool(StrEnum):
    """Infrastructure as Code tool."""

    TERRAFORM = "terraform"
    PULUMI = "pulumi"
    CDK = "cdk"
    CLOUDFORMATION = "cloudformation"
    ANSIBLE = "ansible"


class ContainerRegistry(StrEnum):
    """Container image registry."""

    DOCKERHUB = "dockerhub"
    ECR = "ecr"
    GCR = "gcr"
    GHCR = "ghcr"
    ACR = "acr"


class SecretsManagement(StrEnum):
    """Secrets management solution."""

    ENV_FILE = "env_file"
    VAULT = "vault"
    AWS_SSM = "aws_ssm"
    DOPPLER = "doppler"
    INFISICAL = "infisical"


# Phase 5 enums


class Likelihood(StrEnum):
    """Risk likelihood level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Impact(StrEnum):
    """Risk impact level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConfidenceLevel(StrEnum):
    """Decision confidence level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SecurityCategory(StrEnum):
    """Security requirement category."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    INPUT_VALIDATION = "input_validation"
    AUDIT = "audit"
    TRANSPORT_SECURITY = "transport_security"
