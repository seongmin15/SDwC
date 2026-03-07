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

### 2026-03-05 — T007: Template Engine - post-processing (5 markdown rules)

- **작업**: generation_rules.md §11에 따른 5가지 마크다운 후처리 규칙 구현. Rule 1(빈 섹션 제거 — ##/### 대상, iterative pass로 cascading 처리, Claude-managed 파일 면제), Rule 2(연속 구분선 병합 — line-based scan), Rule 3(과잉 빈 줄 축소 — 3+ → 2), Rule 4(빈 테이블 제거 — header+separator만 있는 테이블), Rule 5(후행 공백 제거). post_process 오케스트레이터가 1→5 순서로 적용.
- **변경된 파일**: src/sdwc_api/engine/postprocess.py (신규), src/sdwc_api/engine/renderer.py (수정 — post_process 통합), tests/unit/test_postprocess.py (신규, 34 tests), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: Rule 2는 regex 대신 line-based scan으로 구현 (3+ 연속 구분선 처리의 신뢰성 확보). Rule 1은 # (h1)은 제외하고 ##/### 만 대상. _is_claude_managed는 basename prefix 매칭으로 구현 (forward-slash 경로 보장). render_all 내부에서 dict comprehension으로 통합하여 API 표면 변경 없음.
- **미완료/후속**: T008 (Template Engine - ZIP packaging & output_contract validation)

### 2026-03-05 — T008: Template Engine - ZIP packaging & output_contract validation

- **작업**: output_contract.md 기반 유효성 검증 (S-2~S-9 구조 검사, C-1~C-7 콘텐츠 검사) + ZIP 패키징 (.sdwc/ 리소스 포함) 구현 완료.
- **변경된 파일**: src/sdwc_api/engine/validator.py (신규), src/sdwc_api/engine/packager.py (신규), src/sdwc_api/exceptions/__init__.py (수정 — OutputContractError 추가), tests/unit/test_validator.py (신규, 51 tests), tests/unit/test_packager.py (신규, 14 tests), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: validator는 engine/ 패키지에 배치 (postprocess와 동일한 순수 함수 패턴). C-4/C-5/C-6/C-7은 postprocess rule 함수 재사용 (rule(content) != content 비교로 안전망 역할). Sequence[ServiceModel] 타입으로 mypy list invariance 해결. .sdwc/ 복사는 per-file try/except (E-5 spec). S-1은 ZIP assembly에서 강제 (dict validation에서 제외).
- **미완료/후속**: T009 (API endpoints - GET /template & POST /validate)

### 2026-03-05 — T009: API endpoints - GET /template & POST /validate

- **작업**: GET /api/v1/template (intake_template.yaml FileResponse 다운로드), POST /api/v1/validate (multipart 업로드 → parse_intake_yaml → RFC 7807 에러 매핑) 엔드포인트 구현 완료.
- **변경된 파일**: src/sdwc_api/routers/intake.py (신규), src/sdwc_api/schemas/responses.py (신규), src/sdwc_api/core/config.py (수정 — SDWC_RESOURCE_DIR 추가), src/sdwc_api/main.py (수정 — intake router 마운트), tests/integration/test_intake.py (신규, 10 tests), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: SDWC_RESOURCE_DIR을 config.py에 추가하여 .sdwc/ 경로를 환경변수로 오버라이드 가능하게 함. B008 ruff 규칙 준수를 위해 File(...) 기본값 대신 UploadFile 타입만 사용. Pydantic ValidationError는 e.errors()를 순회하며 개별 RFC 7807 항목으로 변환.
- **미완료/후속**: T010 (API endpoints - POST /preview & POST /generate)

### 2026-03-06 — T010: API endpoints - POST /preview & POST /generate

- **작업**: POST /api/v1/preview (파일 트리 JSON 반환) 및 POST /api/v1/generate (ZIP 패키징 StreamingResponse 반환) 엔드포인트 구현 완료. 30s asyncio.wait_for 타임아웃, RFC 7807 에러 핸들링 (validation-failed, rendering-failed, request-timeout, output-contract-failed). 통합 테스트 중 발견된 3개 부수 버그 수정.
- **변경된 파일**: src/sdwc_api/routers/intake.py (수정 — preview/generate 엔드포인트 + 공유 헬퍼), src/sdwc_api/schemas/responses.py (수정 — PreviewResponse, ServiceInfo 추가), src/sdwc_api/engine/renderer.py (수정 — ChainableUndefined), src/sdwc_api/engine/validator.py (수정 — C-1 코드블록 제외), src/sdwc_api/engine/postprocess.py (수정 — iteration-until-stable), tests/integration/test_intake.py (수정 — 10개 신규 테스트), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: (1) ChainableUndefined: 템플릿이 optional 필드를 `{% if field.attr %}` 패턴으로 접근 — default Undefined는 AttributeError 발생, ChainableUndefined로 전환. (2) C-1 validator: 코드블록 내 `}}` (Python dict literal)이 false positive — _strip_fenced_code로 code block 제외. (3) postprocess iteration: Rule 4(빈 테이블 제거)가 새 빈 섹션 생성 가능 — 전체 규칙 세트를 iteration-until-stable로 변경.
- **미완료/후속**: T011 (Error handling - RFC 7807 & domain exceptions)

### 2026-03-06 — T011: Error handling - RFC 7807 & domain exceptions

- **작업**: 인라인 try/except 블록을 4개 글로벌 예외 핸들러로 중앙화. SdwcError 베이스에 http_status/error_type/title 클래스 속성 추가. YamlParseError, PipelineTimeoutError, RenderingError 도메인 예외 신규. yaml_parser의 ValueError/TimeoutError → YamlParseError 전환. /preview, /generate 라우트 단순화 (~60줄 중복 제거).
- **변경된 파일**: src/sdwc_api/exceptions/__init__.py (수정), src/sdwc_api/services/yaml_parser.py (수정), src/sdwc_api/core/error_handlers.py (신규), src/sdwc_api/main.py (수정), src/sdwc_api/routers/intake.py (수정), tests/unit/test_yaml_parser.py (수정), tests/unit/test_error_handlers.py (신규, 14 tests), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: (1) 예외 클래스에 RFC 7807 메타데이터를 직접 부착 (매핑 테이블 대신). (2) /validate는 의도적으로 200 OK + {valid: false} 반환 유지 (글로벌 핸들러 미적용). (3) YAML 5s 파싱 타임아웃은 YamlParseError로 처리 (파싱 문제), 30s 파이프라인 타임아웃은 PipelineTimeoutError로 분리.
- **미완료/후속**: T012 (Structured logging - structlog & request middleware)

### 2026-03-06 — T012: Structured logging - structlog & request middleware

- **작업**: structlog JSON 로깅 설정 추출 (core/logging.py), 순수 ASGI 요청 로깅 미들웨어 구현 (middleware/request_logging.py), request_id UUID4 상관관계, /health 제외, error_handlers.py에 request_id 추가.
- **변경된 파일**: src/sdwc_api/core/logging.py (신규), src/sdwc_api/middleware/__init__.py (신규), src/sdwc_api/middleware/request_logging.py (신규), src/sdwc_api/main.py (수정), src/sdwc_api/core/error_handlers.py (수정), tests/unit/test_logging_setup.py (신규, 5 tests), tests/unit/test_request_logging.py (신규, 8 tests), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: (1) BaseHTTPMiddleware 대신 순수 ASGI 미들웨어 사용 — StreamingResponse (/generate)와의 호환성 문제 방지. (2) structlog.contextvars로 request_id 자동 바인딩 — 요청 내 모든 로그에 자동 포함. (3) /health 경로 제외 — 노이즈 감소. (4) setup_logging()을 core/logging.py로 분리 — 테스트에서 재사용 가능.
- **미완료/후속**: T013 (sdwc-web project scaffolding)

### 2026-03-06 — T013: sdwc-web project scaffolding

- **작업**: Vite + React + TypeScript 프로젝트 초기화. Tailwind CSS v4, Zustand v5, Vitest + @testing-library/react, ESLint flat config (typescript-eslint, react-hooks, jsx-a11y), Prettier 설정. coding-standards skill 기반 디렉토리 구조 생성.
- **변경된 파일**: sdwc-web/ (전체 신규 — package.json, vite.config.ts, tsconfig.*.json, eslint.config.js, .prettierrc, src/app/App.tsx, src/app/providers.tsx, src/main.tsx, src/index.css, src/app/App.test.tsx, tests/setup.ts, index.html, .gitignore), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: (1) Tailwind v4 @tailwindcss/vite 플러그인 사용 (postcss.config 불필요). (2) ESLint flat config (eslint.config.js) 채택 — 신규 프로젝트 표준. (3) vitest/config에서 defineConfig import — test 옵션 타입 지원. (4) tsconfig.app.json에서 *.test.tsx 제외 — tsc -b가 vitest 타입 없이도 빌드 가능. (5) 라우터 미설치 — 단일 페이지 앱으로 라우팅 불필요.
- **미완료/후속**: T014 (Web UI - upload flow components)

### 2026-03-06 — T014: Web UI - upload flow components

- **작업**: TemplateDownloadButton (anchor to GET /api/v1/template), FileUploader (drag-drop + file picker with onUpload callback), ValidationResult (success/error/warning 표시, onReset) 3개 컴포넌트 구현. App.tsx에 로컬 상태 기반 idle→uploading→validating→validation_error/validated 전환 로직.
- **변경된 파일**: src/types/api.ts (신규), src/components/TemplateDownloadButton/ (신규, 2 files), src/components/FileUploader/ (신규, 2 files), src/components/ValidationResult/ (신규, 2 files), src/app/App.tsx (수정), src/app/App.test.tsx (수정), tests/setup.ts (수정 — cleanup 추가), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: (1) 컴포넌트는 presentational — API 호출 없이 props로만 동작 (T016에서 Zustand 연결). (2) TemplateDownloadButton은 `<a href download>` — JS fetch 불필요. (3) vitest + @testing-library/react cleanup을 tests/setup.ts에 명시적 afterEach로 추가 (자동 cleanup 미작동 이슈). (4) jsx-a11y 규칙에 따라 `<ul>` 에 redundant role="list" 제거.
- **미완료/후속**: T015 (Web UI - preview & generate flow components)

### 2026-03-06 — T015: Web UI - preview & generate flow components

- **작업**: FileTreePreview (재귀 collapsible TreeNode), GenerateButton (스피너 로딩 상태), ErrorDisplay (RFC 7807 title/detail/status) 3개 컴포넌트 구현. App.tsx를 full 9-state flow로 확장 (idle→uploading→validating→validation_error/previewing→preview_ready→generating→complete/generation_error). useEffect로 preview 자동 호출, blob download로 ZIP 생성, handleReset으로 초기화.
- **변경된 파일**: src/components/FileTreePreview/ (신규, 2 files), src/components/GenerateButton/ (신규, 2 files), src/components/ErrorDisplay/ (신규, 2 files), src/app/App.tsx (수정 — 전체 9-state 흐름), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: (1) FileTreePreview는 재귀 TreeNode 컴포넌트로 구현 — 폴더는 expand/collapse 토글, 파일은 leaf 노드. (2) Preview 호출은 useEffect로 자동 트리거 — uiState==="previewing" 진입 시 발동, cleanup으로 cancelled flag 관리. (3) Generate는 blob + createObjectURL + programmatic click으로 ZIP 다운로드. (4) ErrorDisplay에서 status 0 (network error)은 status line 숨김.
- **미완료/후속**: T016 (Web UI - state management & API integration)

### 2026-03-06 — T016: Web UI - state management & API integration

- **작업**: Zustand 스토어 (useIntakeStore) 생성 — 9-state 머신 + 3개 비동기 액션 (upload, generate, reset). API 서비스 레이어 (intakeApi.ts) — 3개 순수 fetch 함수 (validateYaml, fetchPreview, generateZip). App.tsx를 로컬 상태 + inline fetch에서 스토어 셀렉터/액션으로 리팩터링.
- **변경된 파일**: src/services/intakeApi.ts (신규), src/services/intakeApi.test.ts (신규, 9 tests), src/stores/useIntakeStore.ts (신규), src/stores/useIntakeStore.test.ts (신규, 8 tests), src/app/App.tsx (수정 — 스토어 기반으로 리팩터링), src/app/App.test.tsx (수정 — 스토어 리셋 추가), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: (1) React Query/SWR 미도입 — 단일 선형 플로우에서 캐싱/재검증 불필요, 의존성 추가 요청 승인 필요. Zustand 비동기 액션 + 서비스 레이어로 충분. (2) upload 액션에서 validate → preview 자동 체이닝 — useEffect 의존 제거 (코딩 표준 anti-pattern 해소). (3) validateYaml은 네트워크 에러 시 throw 대신 {valid:false} 반환 — /validate 엔드포인트의 의미론 유지. (4) vi.clearAllMocks()로 모듈 레벨 vi.mock() 호출 카운트 격리.
- **미완료/후속**: T017 (Docker setup - sdwc-api)

### 2026-03-06 — T017: Docker setup - sdwc-api

- **작업**: sdwc-api용 multi-stage Dockerfile 및 .dockerignore 생성. Builder 스테이지에서 poetry export → pip install, runtime 스테이지에서 python:3.12-slim + non-root user. .sdwc/ 템플릿 리소스 포함. HEALTHCHECK 설정.
- **변경된 파일**: sdwc-api/Dockerfile (신규), .dockerignore (신규), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: (1) 빌드 컨텍스트를 프로젝트 루트로 설정 (`docker build -f sdwc-api/Dockerfile .`) — .sdwc/ 템플릿 디렉토리가 sdwc-api/ 외부에 위치하므로. (2) non-root user (appuser:1000) 적용 — 보안 베스트 프랙티스. (3) HEALTHCHECK에 Python urllib 사용 — slim 이미지에 curl 미포함. (4) .dockerignore를 프로젝트 루트에 배치 — 빌드 컨텍스트 루트에서 적용.
- **미완료/후속**: T018 (Docker setup - sdwc-web & k3s manifests)

### 2026-03-06 — T018: Docker setup - sdwc-web & k3s manifests

- **작업**: sdwc-web용 multi-stage Dockerfile (node:20-slim → nginx:alpine), SPA 라우팅 nginx.conf, k3s 배포 매니페스트 (Deployment + Service × 2, Ingress) 생성. infra/ 디렉토리 구조 수립.
- **변경된 파일**: sdwc-web/Dockerfile (신규), sdwc-web/nginx.conf (신규), infra/sdwc-api/deployment.yaml (신규), infra/sdwc-web/deployment.yaml (신규), infra/ingress.yaml (신규), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: (1) nginx.conf에 /api/ reverse proxy 포함 — k3s Ingress 없이도 단독 docker-compose 환경에서 API 라우팅 가능. (2) Ingress에 Traefik annotation 사용 — k3s 기본 Ingress controller. (3) sdwc-web 리소스 제한을 API보다 낮게 설정 (CPU 200m, Memory 128Mi) — 정적 파일 서빙만 수행. (4) HEALTHCHECK에 wget 사용 — nginx:alpine에 curl 미포함이나 wget 내장.
- **미완료/후속**: 전체 T001-T018 태스크 완료. 향후 작업은 05-roadmap 참조.

### 2026-03-06 — T019: Local deployment on k3d

- **작업**: k3d (k3s-in-Docker) 기반 로컬 배포 완료. k3d 설치 (winget), 클러스터 생성 (port 8080:80), Docker 이미지 빌드 및 k3d import, k8s 매니페스트 적용, 엔드투엔드 검증. 배포 중 발견된 3개 버그 수정. README.md에 로컬 배포 절차 문서화.
- **변경된 파일**: infra/sdwc-api/deployment.yaml (image → sdwc-api:local, imagePullPolicy: Never), infra/sdwc-web/deployment.yaml (image → sdwc-web:local, imagePullPolicy: Never), infra/ingress.yaml (Traefik priority 기반 2개 Ingress로 분리), sdwc-api/Dockerfile (poetry-plugin-export 추가, --ignore-installed 추가), sdwc-api/src/sdwc_api/core/config.py (_REPO_ROOT try/except fallback), README.md (Local Deployment 섹션 추가), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: (1) Ingress를 2개로 분리하고 Traefik priority 어노테이션 적용 — 단일 Ingress에서 `/` Prefix가 `/health` Exact보다 우선 매칭되는 문제 해결. (2) config.py에 try/except 추가 — Docker 컨테이너 내 path depth 차이로 IndexError 발생, env var SDWC_RESOURCE_DIR이 이미 설정되어 fallback은 안전. (3) pip --ignore-installed 추가 — Poetry 의존성이 /usr/local에 설치되어 --prefix=/install로 복사되지 않는 문제 해결.
- **미완료/후속**: 없음

### 2026-03-06 — T020: Fix CLAUDE_BASE.md non-ASCII characters

- **작업**: ZIP Review v1.32에서 발견된 CLAUDE_BASE.md 내 non-ASCII 문자 4건 수정. U+2014 (em dash) 3건 -> ASCII hyphen, U+2192 (right arrow) 1건 -> ASCII `->`. .sdwc/CLAUDE_BASE.md (서버 리소스 원본) 및 CLAUDE.md (렌더링 결과) 양쪽 수정.
- **변경된 파일**: .sdwc/CLAUDE_BASE.md (4건 수정), CLAUDE.md (4건 수정), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: 서버 리소스 결함 원칙에 따라 .sdwc/CLAUDE_BASE.md 원본 수정. CLI 환경에서 재렌더링 불가하므로 CLAUDE.md도 직접 수정 (임시 조치). Desktop에서 재렌더링 ZIP 발급 시 근본 조치 완료.
- **미완료/후속**: Desktop에 보고하여 재렌더링 ZIP 발급 요청 필요

### 2026-03-07 — T021: Add k3d deployment scripts

- **작업**: Human이 scripts/ 디렉토리에 k3d 배포 헬퍼 스크립트 5개 추가. deploy.sh (클러스터 생성 + 이미지 빌드 + import + 매니페스트 적용), rebuild.sh (이미지 재빌드 + rollout restart), clean.sh (클러스터 삭제), status.sh (pods/svc/ingress 조회), logs.sh (pod 로그 조회).
- **변경된 파일**: scripts/deploy.sh (신규), scripts/rebuild.sh (신규), scripts/clean.sh (신규), scripts/status.sh (신규), scripts/logs.sh (신규), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: Human이 직접 작성한 스크립트. Section 5.6 절차에 따라 문서 업데이트.
- **미완료/후속**: 없음

### 2026-03-07 — T022-T023: intake_template.yaml mobile enums & optional field guidance

- **작업**: ZIP Review v1.32 발견 사항 2건 해결. T022: 모바일 네이티브 테스트 프레임워크(xctest, espresso, robolectric, flutter_test, detox), 배포 타겟(app_store, play_store, both_stores), CI 도구(xcode_cloud, bitrise, codemagic), CD 도구(fastlane, app_center) enum 추가. T023: 파일 헤더에 미사용 optional 필드 제거 안내 4줄 추가 + 9개 optional 블록에 DELETE 리마인더 코멘트 추가.
- **변경된 파일**: .sdwc/intake_template.yaml (enum 확장 + 안내 추가), sdwc-api/src/sdwc_api/schemas/enums.py (TestFrameworkEnum, DeploymentTarget, CiTool, CdTool 확장), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: (1) web_ui/worker/mobile_app/data_pipeline의 ci.tool, cd.tool에 누락된 enum 주석도 함께 추가 (기존에 backend_api만 있었음). (2) generation_rules.md, output_contract.md는 generic variable path 사용으로 수정 불필요 확인.
- **미완료/후속**: 없음

### 2026-03-07 — T024: Fix intake_template.yaml comment-validation mismatches

- **작업**: Simple 모드 시뮬레이션에서 발견된 Validation 4건 에러의 근본 원인 수정. 템플릿 주석과 Validation 간 불일치 3건 (web_ui connected_endpoints, mobile_app connected_endpoints, observability retention_period) 주석 보정.
- **계획**: 3개 주석 수정 → YAML 파싱 확인 → intake_data.yaml 교차 확인 → non-ASCII 0 확인
- **변경된 파일**: .sdwc/intake_template.yaml (3건 주석 수정), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: intake_data.yaml이 repo에 없어 교차 확인은 템플릿 구조 기준으로 대체. generation_rules.md, output_contract.md는 수정 대상 아님 확인.
- **미완료/후속**: 없음

### 2026-03-07 — T025: GitHub Actions CI Pipeline

- **작업**: GitHub Actions CI 파이프라인 구성. 서비스별 워크플로우 2개 생성 (ci-sdwc-api.yml, ci-sdwc-web.yml). Jenkins → GitHub Actions CI 도구 변경에 따른 문서 업데이트 (04-infrastructure, deployment skills, ADR-6).
- **계획**: 07-workplan T025 수정 → 04-infrastructure CI 컬럼 변경 → ADR-6 추가 → deployment skills 업데이트 → 워크플로우 파일 생성 → 10-changelog 기록
- **변경된 파일**: .github/workflows/ci-sdwc-api.yml (신규), .github/workflows/ci-sdwc-web.yml (신규), docs/common/07-workplan.md, docs/common/04-infrastructure.md, docs/common/02-architecture-decisions.md, skills/sdwc-api/deployment/SKILL.md, skills/sdwc-web/deployment/SKILL.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: (1) 서비스별 별도 워크플로우 — path filter로 불필요한 실행 방지. (2) Poetry 2.1.1 고정 — Dockerfile과 일치. (3) GHA 레이어 캐시 (cache-from/to: type=gha) — Docker 빌드 시간 단축. (4) Short SHA (7자) 태그 — 가독성과 트레이서빌리티 균형.
- **미완료/후속**: PR 머지 후 워크플로우 실행 검증, GHCR 이미지 확인

### 2026-03-07 — T026: Migrate infrastructure to sdwc-platform

- **작업**: infra/ 및 scripts/ 디렉토리를 sdwc-platform 레포로 이관. SDwC에서 삭제. 12-runbook.md CI 컬럼 수정 (jenkins -> github_actions). ADR-7 기록.
- **계획**: sdwc-platform에 manifests/sdwc/ 생성 (deployment.yaml 복사) → ArgoCD/deploy-all.sh 경로 변경 → SDwC에서 infra/, scripts/ 삭제 → README.md 업데이트 → deployment skills IaC 위치 변경 → 12-runbook.md CI 수정 → ADR-7 기록
- **변경된 파일**: [sdwc-platform] manifests/sdwc/sdwc-api/deployment.yaml (신규 복사), manifests/sdwc/sdwc-web/deployment.yaml (신규 복사), argocd/sdwc-app.yaml (수정), scripts/deploy-all.sh (수정), README.md (수정). [SDwC] infra/ (삭제), scripts/ (삭제), README.md (수정), skills/sdwc-api/deployment/SKILL.md (수정), skills/sdwc-web/deployment/SKILL.md (수정), docs/common/02-architecture-decisions.md (ADR-7 추가), docs/common/12-runbook.md (수정), docs/common/07-workplan.md, docs/common/09-working-log.md, docs/common/10-changelog.md
- **의사결정**: (1) ingress.yaml은 sdwc-platform의 platform-ingress.yaml로 대체되어 복사하지 않음. (2) sdwc-platform 먼저 커밋 후 SDwC 변경 — ArgoCD가 매니페스트를 잃지 않도록 순서 보장.
- **미완료/후속**: 없음
