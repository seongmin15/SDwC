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

### Changed
- Section 5.1 Receiving a Task: added pre-coding checklist (step 7) requiring 07-workplan In Progress and 09-working-log plan recording before writing any code (applied to CLAUDE.md and .sdwc/CLAUDE_BASE.md)
- Section 5.8 Completing a Task: added pre-commit doc checklist (step 5) with sub-tasks for 07-workplan, 09-working-log, 10-changelog, and Section 6 trigger docs (applied to CLAUDE.md and .sdwc/CLAUDE_BASE.md)

### Added
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
