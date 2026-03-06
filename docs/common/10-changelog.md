# Changelog

> 이 문서는 Claude가 릴리스 시마다 작성·관리합니다.
> 형식: Keep a Changelog format

---

## [Unreleased]

<!-- Claude: §5.8 작업 완료 시 해당 변경을 [Unreleased]에 기록.
     분류 기준:
     - Added: 새 기능, 새 엔드포인트, 새 엔티티
     - Changed: 기존 동작 변경, 리팩터링
     - Fixed: 버그 수정
     - Removed: 기능/코드 삭제
     한 줄에 "무엇이 어떻게 변했는가"만 간결하게.
     릴리스 시 [Unreleased]를 버전 번호로 전환.
     형식: ## [X.Y.Z] - YYYY-MM-DD -->

### Added
- Web UI state management & API integration: Zustand store (useIntakeStore) with 9-state machine and async actions, API service layer (intakeApi.ts) with validateYaml/fetchPreview/generateZip. App.tsx refactored to use store selectors. 17 new tests (43 total)
- Web UI preview & generate flow: FileTreePreview (recursive collapsible tree), GenerateButton (with spinner state), ErrorDisplay (RFC 7807 title/detail/status). App.tsx extended to full 9-state flow with auto-preview trigger, blob ZIP download, reset. 13 new component tests (26 total)
- Web UI upload flow: TemplateDownloadButton (anchor to GET /template), FileUploader (drag-drop + file picker), ValidationResult (success/error/warning display), App.tsx state transitions (idle/uploading/validating/validation_error/validated), API types (types/api.ts). 13 component tests
- sdwc-web project scaffolding: Vite 7 + React 19 + TypeScript 5.9, Tailwind CSS v4, Zustand v5, Vitest + @testing-library/react, ESLint flat config (typescript-eslint, react-hooks, jsx-a11y), Prettier, path alias @/, API proxy, project structure per coding-standards skill
- Structured logging: setup_logging() with JSON rendering, contextvars merge, configurable log level. Pure ASGI RequestLoggingMiddleware with request_id correlation (UUID4), method/path/status/duration_ms logging, /health exclusion. 13 new unit tests (379 total)

### Changed
- Error handling: centralized inline try/except blocks into 4 global exception handlers (SdwcError, ValidationError, RequestValidationError, unhandled Exception) producing RFC 7807 responses. Simplified /preview and /generate routes by removing ~60 lines of duplicated error handling. Added domain exceptions (YamlParseError, PipelineTimeoutError, RenderingError) with class-level HTTP/RFC7807 metadata.
- Section 5.1 Receiving a Task: added pre-coding checklist (step 7) requiring 07-workplan In Progress and 09-working-log plan recording before writing any code (applied to CLAUDE.md and .sdwc/CLAUDE_BASE.md)
- Section 5.8 Completing a Task: added pre-commit doc checklist (step 5) with sub-tasks for 07-workplan, 09-working-log, 10-changelog, and Section 6 trigger docs (applied to CLAUDE.md and .sdwc/CLAUDE_BASE.md)

### Fixed
- Jinja2 renderer: switched from Undefined to ChainableUndefined to support optional field attribute chaining in templates
- Output contract C-1 check: exclude fenced code blocks to avoid false positives from Python dict literals containing `}}`
- Postprocessor: iterate full rule sequence until stable to handle cross-rule interactions (e.g., empty table removal creating empty sections)

### Added
- API endpoints: POST /api/v1/preview (PreviewResponse with file_tree/file_count/services) and POST /api/v1/generate (StreamingResponse ZIP), 30s asyncio timeout, RFC 7807 error handling, PreviewResponse/ServiceInfo response models (10 new integration tests, 352 total)
- API endpoints: GET /api/v1/template (FileResponse with application/x-yaml) and POST /api/v1/validate (multipart upload, RFC 7807 error format), ValidationErrorItem/ValidationResponse response models, SDWC_RESOURCE_DIR config setting (10 new integration tests, 342 total)
- Output contract validator: 14 check functions (S-2~S-9 structure, C-1~C-7 content), validate_output/validate_or_raise orchestrators, OutputContractError exception with violation collection (51 new tests)
- ZIP packager: build_zip with in-memory ZIP_DEFLATED assembly, project.name root folder, .sdwc/ server resource copy with per-file E-5 warning handling (14 new tests, 332 total)
- Markdown post-processing pipeline: 5 rules (empty sections, consecutive dividers, blank lines, empty tables, trailing whitespace) with Claude-managed file exemption, integrated into render_all (34 new tests, 266 total)
- Template Engine Jinja2 rendering pipeline: create_jinja_env, _make_adr_seq, _discover_templates, _map_output_path, render_all with 4-phase orchestration, SdwcError + FrameworkNotFoundError exceptions (33 new tests, 232 total)
- Template Engine context composition layer: normalize (§10 falsy removal), compose_global_context, compose_service_context, compose_skill_context, ServiceModel type alias (34 new tests, 199 total)
- Project initialized with README.md, .gitignore, git repo, and remote (github.com/seongmin15/SDwC)
- Initial work plan with 18 tasks (T001-T018) in 07-workplan
- sdwc-api project scaffolding: FastAPI + Poetry, src/sdwc_api/ structure, health endpoint, ruff/mypy/pytest config
- Pydantic v2 models for intake_template.yaml phases 1-3: 14 enums, 20+ models covering project identity, goals/scope, users/stakeholders/collaboration (63 unit tests)
- Pydantic v2 models for intake_template.yaml phases 4-6: ~50 enums, Architecture, 5 service types with discriminated union, Deployment, CriticalFlow, Security, Risks (47 new tests, 110 total)
- Pydantic v2 models for intake_template.yaml phases 6-8: 15 new enums, Performance/Availability/Observability/ExternalSystem/Process/CodeQuality/Testing/VersionControl/Evolution/Rollout/Operations models (55 new tests, 165 total)
- Root IntakeData model combining all phases with per_service↔services cross-field validation
- YAML parser with safe_load, 1MB size limit, 5s threading-based timeout
