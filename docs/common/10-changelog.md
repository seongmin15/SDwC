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
- Section 5.8 Completing a Task: added pre-commit doc checklist (step 5) with sub-tasks for 07-workplan, 09-working-log, 10-changelog, and Section 6 trigger docs (applied to CLAUDE.md and .sdwc/CLAUDE_BASE.md)

### Added
- Project initialized with README.md, .gitignore, git repo, and remote (github.com/seongmin15/SDwC)
- Initial work plan with 18 tasks (T001-T018) in 07-workplan
- sdwc-api project scaffolding: FastAPI + Poetry, src/sdwc_api/ structure, health endpoint, ruff/mypy/pytest config
- Pydantic v2 models for intake_template.yaml phases 1-3: 14 enums, 20+ models covering project identity, goals/scope, users/stakeholders/collaboration (63 unit tests)
