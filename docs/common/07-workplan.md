# Work Plan

> This document is the single source of truth (SSOT) for project tasks.
> AI proposes tasks, and they are reflected after user approval.

## Operating Rules

- Each task should be reviewable in ~30 minutes.
- WIP Limit: 2
- Status transitions require user approval.
- History must not be deleted.

## Status Flow

```
Backlog -> Ready -> In Progress -> Review -> Done
                        |    ^
                        v    |
                      Paused

Any active status -> Cancelled
```

- **Paused**: task is temporarily stopped. Only from In Progress.
- **Cancelled**: task is abandoned. Record reason in Result.

## Task Format

```
### T<NNN>: <title>
- Status: Backlog | Ready | In Progress | Review | Paused | Cancelled | Done
- Service: <service name>
- Origin: T<NNN> (optional, when derived from another task)
- Description: <description>
- Acceptance Criteria:
  - [ ] <criterion 1>
  - [ ] <criterion 2>
- Result: (recorded after completion)
```

### Origin Rules

- Record when a task is derived from issues found in another task's Result.
- Omit Origin for initial tasks.

### Result Rules

- Result must be recorded when Status becomes Done or Cancelled.
- All Acceptance Criteria items must be checked before transitioning to Done.
- If some items are split into other tasks, mark as "deferred to T<NNN>" on the original item.
- Include: created files, test results, discovered issues.
- Record issues resolved within the task as well.
- Issues exceeding 30 minutes should be split into a new task.
- Out-of-scope issues move to docs/common/05-roadmap.md.

---

## Tasks

> AI writes the initial task list at project start.

<!-- Claude: This is a hybrid document.
     Template Engine fills Operating Rules, Status Flow, Task Format.
     Claude fills the Tasks section during Init based on docs/common/05-roadmap.md.
     After Init, Claude updates task statuses with user approval.
     Rules:
     - Never delete task history.
     - Always get user approval before status transitions.
     - Keep tasks small (~30 min reviewable).
     - Record Result when Done. -->

### T001: sdwc-api project scaffolding
- Status: Done
- Service: sdwc-api
- Description: Initialize FastAPI project with Poetry. Set up project structure (routers, services, engine packages), configure ruff/mypy, create health endpoint, configure CORS middleware.
- Acceptance Criteria:
  - [x] Poetry project initialized with core dependencies (fastapi, uvicorn, jinja2, pyyaml, pydantic, python-multipart, structlog)
  - [x] Project directory structure follows skills/sdwc-api/coding-standards
  - [x] Health endpoint (`GET /health`) returns 200
  - [x] `poetry run uvicorn` starts the server successfully
  - [x] ruff and mypy configured

### T002: Pydantic models - project & common fields (phases 1-3)
- Status: Done
- Service: sdwc-api
- Description: Define Pydantic v2 models for intake_template.yaml phases 1-3: project, problem, motivation, value_proposition, project_characteristics, goals, non_goals, scope, assumptions, constraints, timeline, budget, glossary, user_personas, anti_personas, stakeholders, collaboration.
- Acceptance Criteria:
  - [x] Models cover all phase 1-3 fields from intake_template.yaml
  - [x] Required field validation with clear error paths
  - [x] CRITICAL enum validation for collaboration.per_service[].mode
  - [x] Unit tests for valid/invalid data
- Result: 14 StrEnum types, 24 Pydantic models (5 phase1, 12 phase2, 7 phase3), 63 unit tests passing. Cross-validation of per_service↔services deferred to T004.

### T003: Pydantic models - services & architecture (phases 4-6)
- Status: Done
- Service: sdwc-api
- Description: Define Pydantic v2 models for phases 4-6: architecture, services (all 5 types: backend_api, web_ui, worker, mobile_app, data_pipeline), critical_flows, security, risks, error_handling.
- Acceptance Criteria:
  - [x] Models cover all 5 service types with their specific fields
  - [x] CRITICAL enum validation (api_style, trigger_type)
  - [x] Nested service-type-specific validation
  - [x] Unit tests for each service type
- Result: ~50 new StrEnum types, Architecture model, 5 service type models with discriminated union (BackendApiService, WebUiService, WorkerService, MobileAppService, DataPipelineService), Deployment shared model, CriticalFlow/Security/Risks models. 47 new unit tests (110 total). Conditional api_style→endpoints/graphql/grpc cross-validation deferred to T004.

### T004: Pydantic models - process & evolution (phases 7-8) + YAML parser
- Status: Ready
- Service: sdwc-api
- Description: Define Pydantic v2 models for phases 7-8: performance, availability, observability, scalability, process, code_quality, testing, version_control, evolution, rollout, operations. Implement YAML parser with safe_load, 1MB size limit, 5s timeout. Create root IntakeData model combining all phases.
- Acceptance Criteria:
  - [ ] Models cover all phase 7-8 fields
  - [ ] CRITICAL enum validation for process.methodology
  - [ ] Root IntakeData model combines all phases
  - [ ] YAML parser uses safe_load with size/timeout limits
  - [ ] Unit tests for parsing and full model validation

### T005: Template Engine - context composition
- Status: Ready
- Service: sdwc-api
- Description: Build context composition layer per generation_rules.md §1-3. Create global context from full intake_data, service context from services[i] with per_service field merge. Handle variable mapping rules.
- Acceptance Criteria:
  - [ ] Global context correctly composed from full intake_data
  - [ ] Service context composed per service with per_service fields merged
  - [ ] Variable mapping matches generation_rules.md §3 specification
  - [ ] Unit tests for both context types

### T006: Template Engine - Jinja2 rendering & custom functions
- Status: Ready
- Service: sdwc-api
- Description: Set up Jinja2 environment with template directories, implement rendering pipeline for CLAUDE_BASE, doc-templates, and skill-templates. Implement custom functions (adr_seq for ADR numbering). Follow generation_rules.md §4-6.
- Acceptance Criteria:
  - [ ] Jinja2 environment configured with correct template directories
  - [ ] CLAUDE_BASE.md renders correctly with global context
  - [ ] doc-templates render with appropriate context (global or service)
  - [ ] skill-templates selected per generation_rules.md §8
  - [ ] adr_seq() produces sequential gap-free numbering
  - [ ] Unit tests for rendering and custom functions

### T007: Template Engine - post-processing (5 markdown rules)
- Status: Ready
- Service: sdwc-api
- Description: Implement markdown post-processing per generation_rules.md §11: remove empty sections, merge consecutive separators, collapse excess blank lines, remove empty tables, strip trailing whitespace. Skip rule 1 for Claude-managed files (07, 09, 10, 11, 12).
- Acceptance Criteria:
  - [ ] All 5 post-processing rules implemented
  - [ ] Claude-managed files exempt from rule 1
  - [ ] Unit tests for each rule with edge cases

### T008: Template Engine - ZIP packaging & output_contract validation
- Status: Ready
- Service: sdwc-api
- Description: Implement ZIP file assembly with correct directory structure. Copy .sdwc/ server resources without rendering. Validate output against output_contract.md (S-1~S-9 structure checks, C-1~C-7 content checks).
- Acceptance Criteria:
  - [ ] ZIP structure matches output_contract.md specification
  - [ ] .sdwc/ resources copied without Jinja2 rendering
  - [ ] Structure validation (S-1~S-9) passes
  - [ ] Content validation (C-1~C-7) passes
  - [ ] Unit tests for ZIP structure and validation

### T009: API endpoints - GET /template & POST /validate
- Status: Ready
- Service: sdwc-api
- Description: Implement GET /api/v1/template (serve intake_template.yaml) and POST /api/v1/validate (parse, validate, return errors/warnings). RFC 7807 error format for validation failures.
- Acceptance Criteria:
  - [ ] GET /template returns intake_template.yaml with correct content-type
  - [ ] POST /validate accepts multipart file upload
  - [ ] Returns {valid, errors, warnings} JSON response
  - [ ] Invalid YAML returns RFC 7807 error with line numbers
  - [ ] Integration tests for both endpoints

### T010: API endpoints - POST /preview & POST /generate
- Status: Ready
- Service: sdwc-api
- Description: Implement POST /api/v1/preview (return file tree structure) and POST /api/v1/generate (run full pipeline, return ZIP). Wire up Template Engine to endpoints. 30s response timeout.
- Acceptance Criteria:
  - [ ] POST /preview returns {file_tree, file_count, services} JSON
  - [ ] POST /generate returns ZIP file with correct content-type
  - [ ] 30s response timeout enforced
  - [ ] Error responses use RFC 7807 format
  - [ ] Integration tests for both endpoints
  - [ ] Swagger docs auto-generated and accurate

### T011: Error handling - RFC 7807 & domain exceptions
- Status: Ready
- Service: sdwc-api
- Description: Implement global exception handler returning RFC 7807 format. Define domain exceptions (ValidationError, RenderingError, FrameworkNotFoundError, etc.) with HTTP status code mapping.
- Acceptance Criteria:
  - [ ] Global exception handler catches all unhandled errors
  - [ ] Domain exceptions map to correct HTTP status codes
  - [ ] All error responses follow RFC 7807 format
  - [ ] Unit tests for error handler

### T012: Structured logging - structlog & request middleware
- Status: Ready
- Service: sdwc-api
- Description: Configure structlog with JSON output. Implement request/response logging middleware with request_id correlation. Follow skills/common/observability.
- Acceptance Criteria:
  - [ ] structlog configured with JSON rendering
  - [ ] Request logging middleware logs method, path, status, duration
  - [ ] request_id correlation across log entries
  - [ ] Log levels follow skills/common/observability rules

### T013: sdwc-web project scaffolding
- Status: Ready
- Service: sdwc-web
- Description: Initialize React + TypeScript project with Vite. Configure Tailwind CSS, Zustand, ESLint, Prettier. Set up project structure following skills/sdwc-web/coding-standards.
- Acceptance Criteria:
  - [ ] Vite project initialized with React + TypeScript
  - [ ] Tailwind CSS configured and working
  - [ ] Zustand installed
  - [ ] ESLint + Prettier configured
  - [ ] Project structure matches skills/sdwc-web/coding-standards
  - [ ] `npm run dev` starts successfully

### T014: Web UI - upload flow components
- Status: Ready
- Service: sdwc-web
- Description: Build TemplateDownloadButton, FileUploader (drag-and-drop + file picker), and ValidationResult components. Handle idle → uploading → validating → validation_error states.
- Acceptance Criteria:
  - [ ] TemplateDownloadButton triggers intake_template.yaml download
  - [ ] FileUploader supports drag-and-drop and file picker
  - [ ] ValidationResult displays validation success or error details
  - [ ] State transitions: idle → uploading → validating → validation_error work correctly
  - [ ] Basic component tests

### T015: Web UI - preview & generate flow components
- Status: Ready
- Service: sdwc-web
- Description: Build FileTreePreview (collapsible tree), GenerateButton, and ErrorDisplay components. Handle previewing → preview_ready → generating → complete → generation_error states.
- Acceptance Criteria:
  - [ ] FileTreePreview displays ZIP structure as collapsible tree
  - [ ] GenerateButton triggers ZIP generation and download
  - [ ] ErrorDisplay shows RFC 7807 error details
  - [ ] State transitions: previewing → preview_ready → generating → complete work correctly
  - [ ] Basic component tests

### T016: Web UI - state management & API integration
- Status: Ready
- Service: sdwc-web
- Description: Create Zustand store managing all 9 UI states. Implement API service layer calling sdwc-api endpoints. Wire components to store and API.
- Acceptance Criteria:
  - [ ] Zustand store manages all 9 states with transitions
  - [ ] API service functions for all 4 endpoints
  - [ ] Components connected to store and API
  - [ ] Loading and error states handled in all flows
  - [ ] Full upload → validate → preview → generate flow works end-to-end

### T017: Docker setup - sdwc-api
- Status: Backlog
- Service: sdwc-api
- Description: Create multi-stage Dockerfile for sdwc-api (python:3.12-slim). Configure .dockerignore, health check probe.
- Acceptance Criteria:
  - [ ] Multi-stage Dockerfile builds successfully
  - [ ] Container runs and serves API correctly
  - [ ] .dockerignore excludes unnecessary files
  - [ ] Health check probe configured

### T018: Docker setup - sdwc-web & k3s manifests
- Status: Backlog
- Service: sdwc-web
- Description: Create multi-stage Dockerfile for sdwc-web (Node:20-slim build, nginx:alpine runtime). Create k3s deployment manifests, service configs, and ingress rules for both services.
- Acceptance Criteria:
  - [ ] sdwc-web Dockerfile builds and serves SPA via nginx
  - [ ] k8s deployment manifests for both services
  - [ ] Ingress configuration for routing
  - [ ] Health check probes configured
