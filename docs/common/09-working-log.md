# 작업 이력

> 이 문서는 Claude가 개발 과정에서 작성·관리합니다.
> 상단 요약 테이블로 전체 흐름을 파악하고, 하단 상세 로그로 작업 간 맥락을 이어갑니다.

---

## 요약


<!-- Claude: §5.8 작업 완료, §5.12 작업 중단/취소 시 한 줄 추가.
     작업 내용은 "무엇을 왜" 중심 1줄 요약.
     상태: 진행중 | 완료 | 중단 | 취소 -->

---

## 상세 로그

<!-- Claude: 작업 완료/중단/취소 시 아래 형식으로 추가.
     한 작업 = 한 엔트리. 세션 구분 불필요.
     "변경된 파일"은 docs/와 코드 모두 포함.
     "미완료/후속"은 다음 작업자(또는 다음 세션의 자신)가 즉시 이어갈 수 있는 수준으로. -->

<!--
### YYYY-MM-DD — 작업 제목

- **작업**: 무엇을 했는가
- **변경된 파일**: 어떤 docs/code가 변경되었는가
- **의사결정**: 내린 결정과 이유
- **미완료/후속**: 다음에 이어할 것
-->

### 2026-03-03 — Project Init

- **작업**: Section 7 Init 완료. 전체 docs/ 및 skills/ 읽기, README.md 생성, .gitignore 생성, git init, 초기 커밋, remote 연결 (https://github.com/seongmin15/SDwC.git), 초기 태스크 목록 작성 (T001-T018).
- **변경된 파일**: README.md (신규), .gitignore (신규), docs/common/07-workplan.md (태스크 목록 추가), docs/common/09-working-log.md (본 엔트리), docs/common/10-changelog.md
- **의사결정**: 태스크를 ~30분 리뷰 가능 단위로 18개로 분할. T017-T018은 Backlog (코어 기능 완료 후 진행).
- **미완료/후속**: T001 (sdwc-api project scaffolding)부터 시작

### 2026-03-03 — T001: sdwc-api project scaffolding

- **작업**: FastAPI 프로젝트 초기화. Poetry 설정, src/sdwc_api/ 구조 생성, health endpoint, ruff/mypy/pytest 설정.
- **변경된 파일**: sdwc-api/ (신규 디렉토리 전체), .gitignore (poetry.lock 제외 해제), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: coding-standards skill에 따라 `src/sdwc_api/` 구조 채택 (`app/` 대신). DB/ORM/auth 관련 디렉토리 생략. poetry.lock 커밋을 위해 .gitignore 수정.
- **미완료/후속**: T002 (Pydantic models - phases 1-3)

### 2026-03-05 — T002: Pydantic models - project & common fields (phases 1-3)

- **작업**: Phase 1-3 intake_template.yaml 필드에 대한 Pydantic v2 모델 정의. StrEnum 기반 14개 enum, Phase 1 (Project, Problem, Motivation, ValueProposition, ProjectCharacteristic), Phase 2 (Goal, Goals, NonGoal, Scope, Assumption, Constraint, Timeline, Budget, GlossaryEntry 등), Phase 3 (UserPersona, AntiPersona, Stakeholder, Collaboration 등) 모델 구현. 63개 단위 테스트 작성.
- **변경된 파일**: src/sdwc_api/schemas/enums.py (신규), schemas/phase1.py (신규), schemas/phase2.py (신규), schemas/phase3.py (신규), schemas/__init__.py (수정), tests/unit/test_phase1_models.py (신규), tests/unit/test_phase2_models.py (신규), tests/unit/test_phase3_models.py (신규), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: per_service[].service ↔ services[].name 교차 검증은 T004 (root IntakeData 모델)에서 구현 예정 (services는 phase 4-6 소속). Python 3.12+ StrEnum 사용. 파일을 phase별로 분리하여 T003/T004와 일관된 구조 유지.
- **미완료/후속**: T003 (Pydantic models - phases 4-6)

### 2026-03-05 — T003: Pydantic models - services & architecture (phases 4-6)

- **작업**: Phase 4-6 intake_template.yaml 필드에 대한 Pydantic v2 모델 정의. ~50개 신규 StrEnum, Architecture 모델, 5개 서비스 타입 모델 (BackendApiService, WebUiService, WorkerService, MobileAppService, DataPipelineService) with discriminated union, Deployment 공유 모델, CriticalFlow/Security/Risks 모델. 47개 신규 단위 테스트 (누적 110개).
- **변경된 파일**: schemas/enums.py (수정), schemas/phase4_architecture.py (신규), schemas/phase4_services.py (신규), schemas/phase5.py (신규), tests/unit/test_phase4_architecture_models.py (신규), tests/unit/test_phase4_services_models.py (신규), tests/unit/test_phase5_models.py (신규), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: 서비스 타입별 Language/Framework enum 분리 (BackendLanguage, WebLanguage 등). Pydantic discriminated union으로 type 필드 기반 서비스 자동 선택. api_style→endpoints/graphql/grpc 조건부 필수 검증은 T004 root 모델에서 처리 예정. PageTransition/ScreenTransition의 "from" 필드는 Field(alias="from") 사용.
- **미완료/후속**: T004 (Pydantic models - phases 7-8 + YAML parser)

### 2026-03-05 — Ad-hoc: Section 5.8 프로세스 개선

- **작업**: Completing a Task 절차에 pre-commit doc checklist (step 5) 추가. 커밋 전 반드시 확인할 항목을 서브태스크로 명시: 07-workplan Done/AC/Result, 09-working-log 완료 기록, 10-changelog 기록, Section 6 트리거 문서. CLAUDE.md와 .sdwc/CLAUDE_BASE.md 양쪽 반영.
- **변경된 파일**: CLAUDE.md, .sdwc/CLAUDE_BASE.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: 사용자 피드백 반영 — T002 완료 시 workplan Done 갱신 및 문서 업데이트 누락 방지를 위한 명시적 체크리스트 절차 추가.
- **미완료/후속**: 없음

### 2026-03-05 — T004: Pydantic models - phases 6-8 + YAML parser

- **작업**: Phase 6-8 Pydantic v2 모델 정의 (Performance, Availability, Observability, ExternalSystem, Process, CodeQuality, Testing, VersionControl, Evolution, Rollout, Operations), root IntakeData 모델 (전 phase 통합 + per_service↔services 교차 검증), YAML 파서 (safe_load, 1MB 제한, 5s 타임아웃) 구현 완료.
- **변경된 파일**: schemas/enums.py (수정 - 15개 신규 enum), schemas/phase6.py (신규), schemas/phase7.py (신규), schemas/phase8.py (신규), schemas/intake.py (신규), services/yaml_parser.py (신규), tests/unit/test_phase6_models.py (신규), tests/unit/test_phase7_models.py (신규), tests/unit/test_phase8_models.py (신규), tests/unit/test_intake_model.py (신규), tests/unit/test_yaml_parser.py (신규), pyproject.toml (types-PyYAML 추가), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: scalability는 plan 명세대로 `str | None` 유지 (template는 nested 구조이나 plan이 승인됨). ExternalSystem.reliability는 Likelihood enum 재사용. FutureFeature.planned_phase는 PlannedPhase enum 재사용. Windows 환경에서 signal.SIGALRM 미지원으로 threading 기반 타임아웃 구현. types-PyYAML dev 의존성 추가 (mypy 타입 체크용).
- **미완료/후속**: T005 (Template Engine - context composition)

### 2026-03-05 — Ad-hoc: Section 5.1 프로세스 개선

- **작업**: Receiving a Task 절차에 pre-coding checklist (step 7) 추가. 코드 작성 전 반드시 07-workplan In Progress 전환 및 09-working-log 계획 기록을 완료하도록 명시. CLAUDE.md와 .sdwc/CLAUDE_BASE.md 양쪽 반영.
- **변경된 파일**: CLAUDE.md, .sdwc/CLAUDE_BASE.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: T003 진행 시 workplan In Progress 전환 누락 방지를 위한 명시적 체크리스트 형태로 변경.
- **미완료/후속**: 없음

### 2026-03-05 — T005: Template Engine - context composition

- **작업**: generation_rules.md §1-3, §10에 따른 컨텍스트 구성 레이어 구현. normalize 함수 (falsy 값 재귀 제거, _REMOVE sentinel 패턴), compose_global_context (IntakeData → dict), compose_service_context (ServiceModel → dict), compose_skill_context (ServiceModel + PerServiceCollaboration → dict) 4개 함수. ServiceModel 타입 별칭 정의.
- **변경된 파일**: src/sdwc_api/engine/context.py (신규), tests/unit/test_context.py (신규, 34 tests), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: normalize는 _REMOVE sentinel 객체로 "제거 대상"을 구분하여 False/0 보호와 재귀 cascade를 단순하게 구현. ServiceModel은 Union 대신 `X | Y` 문법 사용 (ruff UP007). compose_skill_context에서 collab_dict.pop("service") 로 name-matcher 키 제거.
- **미완료/후속**: T006 (Template Engine - Jinja2 rendering & custom functions)

### 2026-03-05 — T006: Template Engine - Jinja2 rendering & custom functions

- **작업**: generation_rules.md §4-6, §8-9에 따른 Jinja2 렌더링 파이프라인 구현. Jinja2 환경 설정 (Markdown 최적화: trim_blocks, lstrip_blocks, keep_trailing_newline, autoescape=False), adr_seq() 커스텀 함수 (closure 기반 순차 번호), 템플릿 탐색 (_discover_templates), 출력 경로 매핑 (_map_output_path, §9), 4단계 render_all 오케스트레이터 (CLAUDE.md → common docs → common skills → per-service). SdwcError 기반 예외 + FrameworkNotFoundError 도메인 예외.
- **변경된 파일**: src/sdwc_api/engine/renderer.py (신규), src/sdwc_api/exceptions/__init__.py (수정), tests/unit/test_renderer.py (신규, 33 tests), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: Jinja2 Undefined (기본값)으로 {{ mermaid_erd }} 등 미구현 변수가 빈 문자열로 렌더링되도록 허용 (T006 범위). _map_output_path에서 forward slash 강제 (Windows 호환). FrameworkNotFoundError를 SdwcError 하위 클래스로 설계하여 T011 RFC 7807 매핑에 활용 가능.
- **미완료/후속**: T007 (Template Engine - post-processing)
