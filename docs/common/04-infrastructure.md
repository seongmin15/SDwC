# 인프라 및 운영

---

## 1. 배포

### 서비스별 배포 개요

| 서비스 | 배포 대상 | CI | CD | 컨테이너 레지스트리 | 시크릿 관리 |
|--------|----------|-----|-----|---------------------|-----------|
| sdwc-api | kubernetes | jenkins | argocd | ghcr | env_file |
| sdwc-web | kubernetes | jenkins | argocd | ghcr | env_file |

> 배포 명령어, Dockerfile 작성, CI/CD 파이프라인 설정 등 상세 규칙은 skills/{service}/deployment/ 참조

---

## 2. 관측성

| 항목 | 도구 |
|------|------|
| 로깅 | structlog (구조화: True) |
| 메트릭 |  |
| 트레이싱 |  (활성: False) |

### 헬스체크

| 엔드포인트 | 점검 항목 |
|-----------|---------|
| /health | API server running, template files accessible |

> 로그 레벨 기준, 메트릭 네이밍, 마스킹 패턴 등 상세 규칙은 skills/common/observability/ 참조

---

## 3. 가용성 및 확장성


### 단일 장애점

- Single k3s node on Windows WSL2


---

## 4. 성능 요구사항

- **예상 동시 사용자**: 1-5

### 응답 시간 목표

| 엔드포인트/플로우 | P50 | P99 |
|-----------------|-----|-----|
| GET /api/v1/template | 100ms | 500ms |
| POST /api/v1/validate | 500ms | 1s |
| POST /api/v1/preview | 500ms | 1s |
| POST /api/v1/generate | 3s | 10s |


---

## 5. 개발 프로세스

- **방법론**: kanban
- **WIP 제한**: 2
- **태스크 리뷰**: 30분

### 완료 정의

- Code passes all tests
- Swagger docs updated for API changes
- Structured logs added for new error paths

---

## 6. 코딩 표준 (요약)

| 언어 | 스타일 가이드 | 린터 | 포매터 |
|------|-------------|------|--------|
| python | PEP 8 | ruff | ruff |
| typescript | ESLint recommended | eslint | prettier |

- **커밋 컨벤션**: conventional

### 코드 리뷰

- **필수**: True
- **최소 리뷰어**: 1
- **자동 머지**: False

### 문서화

- **코드 주석**: Docstring for public API only
- **ADR 사용**: Record every major tech decision

> 상세 규칙은 skills/ 참조

---

## 7. 버전 관리 (요약)

- **브랜치 전략**: github_flow
- **설명**: main + feature branches. PR required for merge
- **저장소 구조**: monorepo

### PR 정책

- **생성자**: both
- **템플릿 필수**: True
- **스쿼시 머지**: True

> 상세 규칙은 skills/git/SKILL.md 참조

<!-- Claude: 수정/추가 시 기존 섹션 구조와 형식을 유지. -->
