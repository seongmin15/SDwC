# 요구사항

---

## 1. 핵심 목표

| 목표 | 측정 기준 | 우선순위 |
|------|----------|---------|
| Generate complete project documentation (CLAUDE.md + docs + skills) from YAML input | All 26 output files generated correctly for any valid intake_data.yaml | P0 |
| Support all 34 frameworks across 5 service types | Every framework in the supported list produces valid skill-templates | P0 |
| Provide web UI for the full workflow (upload -> validate -> preview -> download) | User can complete the entire flow without CLI or API knowledge | P0 |

---

## 2. 성공 시나리오

A developer fills in intake_template.yaml with an AI agent, uploads it to SDwC, previews the output, and downloads a ZIP containing all project documentation ready for Claude Code

### 성공 지표

| 지표 | 현재 값 | 목표 값 | 측정 방법 |
|------|--------|--------|----------|
| Documentation generation success rate | N/A | 99%+ | Error logs from /generate endpoint |

---

## 3. 비목표

| 비목표 | 근거 | 재검토 시점 |
|--------|------|-----------|
| Code generation | SDwC generates documentation, not application code. Code writing is Claude Code's responsibility after receiving the generated docs |  |
| Post-generation document synchronization | Once the ZIP is delivered, document maintenance is handled by Claude following CLAUDE.md rules. SDwC is a one-time generation tool | v2 if users request re-generation with updated intake |
| Framework tutorials or learning content | Skills contain project rules, not how-to guides. Claude already knows framework specifics |  |
| Intake authoring guidance within SDwC | Intake filling is done with various AI agents before SDwC. SDwC only handles the conversion step |  |

---

## 4. 범위

### 4.1 포함 (In-Scope)

| 기능 | 사용자 스토리 | 우선순위 | 복잡도 |
|------|-------------|---------|--------|
| Template Engine | As a developer, I want my intake_data.yaml to be automatically converted into a complete documentation package | must | L |
| FastAPI endpoints | As a developer, I want API endpoints to validate, preview, and generate documentation | must | M |
| Intake validation with detailed error messages | As a developer, I want clear error messages when my intake_data.yaml has issues | must | M |
| ZIP preview | As a developer, I want to preview the file structure and content before downloading | must | M |
| Web UI (single-page upload flow) | As a developer, I want a simple web interface to upload YAML and download the ZIP | must | L |
| Intake template download | As a developer, I want to download the blank intake_template.yaml from the web UI | must | S |
| Error logging | As an operator, I want structured logs to diagnose generation failures within 5 minutes | must | M |
| Swagger documentation | As a developer, I want auto-generated API documentation | must | S |
| 34 framework skill-templates | As a developer using any of the 34 supported frameworks, I want framework-specific coding standards and rules | must | XL |
| Intake example files | As a developer, I want sample intake_data.yaml files for common framework combinations to understand the format | should | M |

### 4.2 제외 (Out-of-Scope)

| 기능 | 제외 사유 | 예정 시점 |
|------|----------|----------|
| CLI tool | Web UI covers the primary use case. CLI adds maintenance overhead | v2 |
| Generation history storage | Requires database, increases complexity. v1 is stateless | v2 |
| Intake diff | Depends on generation history feature | v2 |

---

## 5. 가정

| 가정 | 틀리면? | 검증 계획 |
|------|--------|----------|
| Users will fill intake_template.yaml with help from an AI agent before uploading | Users may upload incomplete or poorly structured YAML, increasing validation error rates | Provide sample intake files and clear validation error messages |
| 34 frameworks cover the majority of use cases | Users with unsupported frameworks cannot use SDwC | Monitor requested but unsupported frameworks via error logs |
| Jinja2 can handle all template rendering requirements including custom helpers | May need to implement additional custom filters or switch rendering approach | Validate during Phase 3-2 template migration |

---

## 6. 제약 조건

| 제약 | 출처 | 협상 가능 |
|------|------|----------|
| Zero infrastructure cost for v1 | business | no |
| Single developer (human + Claude Code) | business | no |

### 일정

- **데드라인**:
- **이유**:
- **유연성**: flexible

### 예산

- **월 운영 예산**: 0
- **일회성 예산**: 0
- **제약**:
  - Self-hosted on existing Windows PC
  - Free tier services only (ghcr, GitHub)

<!-- Claude: 수정/추가 시 기존 섹션 구조와 형식을 유지. -->
