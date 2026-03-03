# 아키텍처 결정

---

## 1. 아키텍처 패턴

- **패턴**: monolith
- **선택 이유**: Two independent services (API + Web) each simple enough to be standalone monoliths. Microservices overhead unjustified for this scale

- **내부 스타일**: layered
- **내부 스타일 이유**: FastAPI's natural structure: router -> service -> engine. Service Layer Architecture is the 2025 production standard for FastAPI

### 설계 원칙

- Stateless processing -- no server-side state between requests
- Single source of truth -- templates and rules define all generation behavior
- Fail fast with clear errors -- validation before processing

---

## 2. 시스템 구성

### 서비스 목록

| 서비스명 | 타입 | 책임 | 언어/프레임워크 |
|---------|------|------|---------------|
| sdwc-api | backend_api | Validate intake YAML, render templates via Jinja2 Template Engine, and deliver generated documentation as ZIP | python + fastapi |
| sdwc-web | web_ui | Single-page web interface for uploading intake YAML, previewing output, and downloading generated ZIP | typescript + react |

### 서비스 간 통신

| 출발 | 도착 | 프로토콜 | 동기/비동기 |
|------|------|---------|-----------|
| sdwc-api | sdwc-web | http | sync |
| sdwc-web | sdwc-api | http | sync |


---

## 3. 핵심 라이브러리

### sdwc-api

| 이름 | 용도 | 버전 제약 |
|------|------|----------|
| Jinja2 | Template rendering engine for doc-templates, CLAUDE_BASE, and skill-templates |  |
| PyYAML | Parse intake_data.yaml uploads |  |
| pydantic | Intake validation with detailed error messages, request/response schemas |  |
| uvicorn | ASGI server |  |
| python-multipart | File upload handling |  |
| structlog | Structured JSON logging |  |

---

## 4. 영감 및 참조

- Convertio (single-page file conversion UX pattern)

---

## 5. ADR 로그


### ADR-1: 아키텍처 패턴

- **결정**: monolith
- **맥락**: Two independent services (API + Web) each simple enough to be standalone monoliths. Microservices overhead unjustified for this scale
- **검토한 대안**:

| 대안 | 장점 | 단점 | 탈락 사유 |
|------|------|------|----------|
| microservices | Independent scaling, technology flexibility | Unnecessary complexity for 2 simple services, operational overhead | SDwC is a stateless conversion tool with minimal inter-service communication |

- **상태**: 확정

---

### ADR-2: sdwc-api 기술 스택

- **결정**: python + fastapi + poetry
- **맥락**: Async-first, automatic OpenAPI/Swagger docs, Pydantic integration for validation, Python ecosystem for Jinja2 templating
- **빌드 도구 선택 이유**: Dependency locking via poetry.lock, reproducible builds, pyproject.toml single config

- **검토한 대안**:

| 대안 | 탈락 사유 |
|------|----------|
| django | Too heavy for a stateless API with no DB. ORM and admin panel unnecessary |
| express | Would require Node.js Handlebars (no migration benefit) or separate Jinja2 integration |

- **상태**: 확정

---


### ADR-3: sdwc-api 배포 방식

- **결정**: kubernetes
- **맥락**: k8s deployment practice on local Windows WSL2 + k3s environment

- **검토한 대안**:

| 대안 | 탈락 사유 |
|------|----------|
| docker_compose | Misses the goal of practicing k8s deployment and GitOps workflows |
| cloud_run | Zero-cost constraint -- prefer self-hosted on existing hardware |

- **상태**: 확정

---

### ADR-4: sdwc-web 기술 스택

- **결정**: typescript + react + vite
- **맥락**: Largest ecosystem, component reusability, strong TypeScript support, shadcn/ui component library availability
- **빌드 도구 선택 이유**: Fast HMR, modern default for React projects in 2026, simple configuration

- **검토한 대안**:

| 대안 | 탈락 사유 |
|------|----------|
| vue | Smaller ecosystem for UI component libraries compared to React |
| next | SSR/SSG unnecessary for a single-page tool with no SEO requirements |

- **상태**: 확정

---


### ADR-5: sdwc-web 배포 방식

- **결정**: kubernetes
- **맥락**: Same k3s cluster as sdwc-api, consistent deployment practice

- **검토한 대안**:

| 대안 | 탈락 사유 |
|------|----------|
| vercel | Zero-cost constraint and k8s practice goal |

- **상태**: 확정

---


<!-- Claude: 수정/추가 시 기존 섹션 구조와 형식을 유지.
     ADR 번호는 이 문서의 마지막 ADR 번호 + 1로 채번.
     형식: ### ADR-NNN: 제목 → 결정/맥락/대안/상태.
     상태 값: 확정 | 제안 | 폐기 -->
