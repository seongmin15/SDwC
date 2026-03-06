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
- Status: Done
- Service: sdwc-api
- Description: Define Pydantic v2 models for phases 7-8: performance, availability, observability, scalability, process, code_quality, testing, version_control, evolution, rollout, operations. Implement YAML parser with safe_load, 1MB size limit, 5s timeout. Create root IntakeData model combining all phases.
- Acceptance Criteria:
  - [x] Models cover all phase 7-8 fields
  - [x] CRITICAL enum validation for process.methodology
  - [x] Root IntakeData model combines all phases
  - [x] YAML parser uses safe_load with size/timeout limits
  - [x] Unit tests for parsing and full model validation
- Result: 15 new StrEnum types (phase 6-8), 28 new Pydantic models across phase6.py/phase7.py/phase8.py, root IntakeData model with per_service↔services cross-validation, YAML parser with 1MB/5s limits and threading-based timeout. 55 new unit tests (165 total). Added types-PyYAML dev dependency for mypy.

### T005: Template Engine - context composition
- Status: Done
- Service: sdwc-api
- Description: Build context composition layer per generation_rules.md §1-3. Create global context from full intake_data, service context from services[i] with per_service field merge. Handle variable mapping rules.
- Acceptance Criteria:
  - [x] Global context correctly composed from full intake_data
  - [x] Service context composed per service with per_service fields merged
  - [x] Variable mapping matches generation_rules.md §3 specification
  - [x] Unit tests for both context types
- Result: 4 functions in engine/context.py (normalize, compose_global_context, compose_service_context, compose_skill_context), ServiceModel type alias. 34 new unit tests (199 total). Normalize implements §10 falsy removal with False/0 protection and recursive cascade. Skill context merges service + per_service collaboration fields.

### T006: Template Engine - Jinja2 rendering & custom functions
- Status: Done
- Service: sdwc-api
- Description: Set up Jinja2 environment with template directories, implement rendering pipeline for CLAUDE_BASE, doc-templates, and skill-templates. Implement custom functions (adr_seq for ADR numbering). Follow generation_rules.md §4-6.
- Acceptance Criteria:
  - [x] Jinja2 environment configured with correct template directories
  - [x] CLAUDE_BASE.md renders correctly with global context
  - [x] doc-templates render with appropriate context (global or service)
  - [x] skill-templates selected per generation_rules.md §8
  - [x] adr_seq() produces sequential gap-free numbering
  - [x] Unit tests for rendering and custom functions
- Result: 7 functions in engine/renderer.py (_make_adr_seq, create_jinja_env, _discover_templates, _map_output_path, _render_template, _find_per_service, render_all). SdwcError base exception + FrameworkNotFoundError in exceptions/__init__.py. 4-phase render pipeline (CLAUDE.md → common docs → common skills → per-service). 33 new unit tests (232 total). All ruff/mypy/pytest checks pass.

### T007: Template Engine - post-processing (5 markdown rules)
- Status: Done
- Service: sdwc-api
- Description: Implement markdown post-processing per generation_rules.md §11: remove empty sections, merge consecutive separators, collapse excess blank lines, remove empty tables, strip trailing whitespace. Skip rule 1 for Claude-managed files (07, 09, 10, 11, 12).
- Acceptance Criteria:
  - [x] All 5 post-processing rules implemented
  - [x] Claude-managed files exempt from rule 1
  - [x] Unit tests for each rule with edge cases
- Result: 5 rule functions + post_process orchestrator in engine/postprocess.py. Integrated into render_all() via dict comprehension. Claude-managed file detection by basename prefix. Rule 1 iterates until stable for cascading empty sections. 34 new unit tests (266 total). All ruff/mypy/pytest checks pass.

### T008: Template Engine - ZIP packaging & output_contract validation
- Status: Done
- Service: sdwc-api
- Description: Implement ZIP file assembly with correct directory structure. Copy .sdwc/ server resources without rendering. Validate output against output_contract.md (S-1~S-9 structure checks, C-1~C-7 content checks).
- Acceptance Criteria:
  - [x] ZIP structure matches output_contract.md specification
  - [x] .sdwc/ resources copied without Jinja2 rendering
  - [x] Structure validation (S-1~S-9) passes
  - [x] Content validation (C-1~C-7) passes
  - [x] Unit tests for ZIP structure and validation
- Result: engine/validator.py with 14 check functions (S-2~S-9, C-1~C-7) + validate_output/validate_or_raise orchestrators, engine/packager.py with build_zip (in-memory ZIP_DEFLATED, .sdwc/ per-file E-5 warning), OutputContractError exception. C-4/C-5/C-6/C-7 reuse postprocess rule functions as safety net. 66 new unit tests (332 total). All ruff/mypy/pytest pass.

### T009: API endpoints - GET /template & POST /validate
- Status: Done
- Service: sdwc-api
- Description: Implement GET /api/v1/template (serve intake_template.yaml) and POST /api/v1/validate (parse, validate, return errors/warnings). RFC 7807 error format for validation failures.
- Acceptance Criteria:
  - [x] GET /template returns intake_template.yaml with correct content-type
  - [x] POST /validate accepts multipart file upload
  - [x] Returns {valid, errors, warnings} JSON response
  - [x] Invalid YAML returns RFC 7807 error with line numbers
  - [x] Integration tests for both endpoints
- Result: routers/intake.py with GET /api/v1/template (FileResponse, application/x-yaml) and POST /api/v1/validate (multipart upload, parse_intake_yaml, RFC 7807 error mapping). schemas/responses.py with ValidationErrorItem + ValidationResponse models. core/config.py with SDWC_RESOURCE_DIR setting. 10 new integration tests (342 total). All ruff/mypy/pytest pass.

### T010: API endpoints - POST /preview & POST /generate
- Status: Done
- Service: sdwc-api
- Description: Implement POST /api/v1/preview (return file tree structure) and POST /api/v1/generate (run full pipeline, return ZIP). Wire up Template Engine to endpoints. 30s response timeout.
- Acceptance Criteria:
  - [x] POST /preview returns {file_tree, file_count, services} JSON
  - [x] POST /generate returns ZIP file with correct content-type
  - [x] 30s response timeout enforced
  - [x] Error responses use RFC 7807 format
  - [x] Integration tests for both endpoints
  - [x] Swagger docs auto-generated and accurate
- Result: routers/intake.py에 POST /preview (PreviewResponse JSON), POST /generate (StreamingResponse ZIP) 추가. schemas/responses.py에 PreviewResponse, ServiceInfo 모델 추가. 30s asyncio.wait_for 타임아웃 적용. RFC 7807 에러 (validation-failed, rendering-failed, request-timeout, output-contract-failed). 10개 신규 integration tests (352 total). 부수 수정: renderer.py에 ChainableUndefined (optional 필드 Jinja2 호환), validator.py C-1 코드블록 false positive 수정, postprocess.py 교차 규칙 iteration-until-stable.

### T011: Error handling - RFC 7807 & domain exceptions
- Status: Done
- Service: sdwc-api
- Description: Implement global exception handler returning RFC 7807 format. Define domain exceptions (ValidationError, RenderingError, FrameworkNotFoundError, etc.) with HTTP status code mapping.
- Acceptance Criteria:
  - [x] Global exception handler catches all unhandled errors
  - [x] Domain exceptions map to correct HTTP status codes
  - [x] All error responses follow RFC 7807 format
  - [x] Unit tests for error handler
- Result: 4 global exception handlers in core/error_handlers.py (SdwcError, ValidationError, RequestValidationError, unhandled Exception). 3 new domain exceptions (YamlParseError, PipelineTimeoutError, RenderingError) with class-level RFC 7807 metadata. Existing exceptions (FrameworkNotFoundError, OutputContractError) enhanced with RFC 7807 attrs. yaml_parser ValueError/TimeoutError → YamlParseError. /preview and /generate simplified (~60 lines removed). 14 new unit tests (366 total). All ruff/mypy/pytest pass.

### T012: Structured logging - structlog & request middleware
- Status: Done
- Service: sdwc-api
- Description: Configure structlog with JSON output. Implement request/response logging middleware with request_id correlation. Follow skills/common/observability.
- Acceptance Criteria:
  - [x] structlog configured with JSON rendering
  - [x] Request logging middleware logs method, path, status, duration
  - [x] request_id correlation across log entries
  - [x] Log levels follow skills/common/observability rules
- Result: core/logging.py with setup_logging() (JSON renderer, contextvars, timestamper, configurable log level). middleware/request_logging.py with pure ASGI RequestLoggingMiddleware (request_id UUID4, method/path/status/duration_ms, /health excluded, structlog contextvars binding). error_handlers.py updated with request_id in unhandled error logs. 13 new unit tests (379 total). All ruff/mypy/pytest pass.

### T013: sdwc-web project scaffolding
- Status: Done
- Service: sdwc-web
- Description: Initialize React + TypeScript project with Vite. Configure Tailwind CSS, Zustand, ESLint, Prettier. Set up project structure following skills/sdwc-web/coding-standards.
- Acceptance Criteria:
  - [x] Vite project initialized with React + TypeScript
  - [x] Tailwind CSS configured and working
  - [x] Zustand installed
  - [x] ESLint + Prettier configured
  - [x] Project structure matches skills/sdwc-web/coding-standards
  - [x] `npm run dev` starts successfully
- Result: Vite 7 + React 19 + TypeScript 5.9 project. Tailwind CSS v4 via @tailwindcss/vite plugin. Zustand v5 installed. ESLint flat config with typescript-eslint, react-hooks, jsx-a11y. Prettier (double quotes, trailing commas, 100 chars). Vitest + @testing-library/react + jsdom. Path alias @/ = src/. Proxy /api → localhost:8000. Project structure per coding-standards skill. 1 test passing. Build, lint, format all pass.

### T014: Web UI - upload flow components
- Status: Done
- Service: sdwc-web
- Description: Build TemplateDownloadButton, FileUploader (drag-and-drop + file picker), and ValidationResult components. Handle idle → uploading → validating → validation_error states.
- Acceptance Criteria:
  - [x] TemplateDownloadButton triggers intake_template.yaml download
  - [x] FileUploader supports drag-and-drop and file picker
  - [x] ValidationResult displays validation success or error details
  - [x] State transitions: idle → uploading → validating → validation_error work correctly
  - [x] Basic component tests
- Result: 3 components (TemplateDownloadButton, FileUploader with drag-drop + file picker, ValidationResult with error/warning display). App.tsx wired with local state for idle/uploading/validating/validation_error/validated transitions. API types in types/api.ts. Test setup fixed with explicit cleanup. 13 tests passing. Build, lint, format all clean.

### T015: Web UI - preview & generate flow components
- Status: Done
- Service: sdwc-web
- Description: Build FileTreePreview (collapsible tree), GenerateButton, and ErrorDisplay components. Handle previewing → preview_ready → generating → complete → generation_error states.
- Acceptance Criteria:
  - [x] FileTreePreview displays ZIP structure as collapsible tree
  - [x] GenerateButton triggers ZIP generation and download
  - [x] ErrorDisplay shows RFC 7807 error details
  - [x] State transitions: previewing → preview_ready → generating → complete work correctly
  - [x] Basic component tests
- Result: 3 new components (FileTreePreview with recursive collapsible TreeNode, GenerateButton with spinner state, ErrorDisplay with RFC 7807 title/detail/status). App.tsx extended to full 9-state flow (idle→uploading→validating→validation_error/previewing→preview_ready→generating→complete/generation_error) with useEffect auto-trigger for preview, blob download for generate, and reset flow. 13 new component tests (26 total). Build, lint, format all pass.

### T016: Web UI - state management & API integration
- Status: Done
- Service: sdwc-web
- Description: Create Zustand store managing all 9 UI states. Implement API service layer calling sdwc-api endpoints. Wire components to store and API.
- Acceptance Criteria:
  - [x] Zustand store manages all 9 states with transitions
  - [x] API service functions for all 4 endpoints
  - [x] Components connected to store and API
  - [x] Loading and error states handled in all flows
  - [x] Full upload → validate → preview → generate flow works end-to-end
- Result: Zustand store (useIntakeStore) with 9-state machine, 3 async actions (upload, generate, reset). API service layer (intakeApi.ts) with 3 pure fetch functions (validateYaml, fetchPreview, generateZip). App.tsx refactored from ~170 lines of local state + fetch to ~100 lines using store selectors. Upload action auto-chains validate → preview (eliminated useEffect anti-pattern). 17 new tests (43 total). Build, lint, format all pass.

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
