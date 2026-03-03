# API 계약

---

## 1. API 개요

- **스타일**: rest
- **선택 이유**: Simple CRUD-like operations (upload, validate, preview, generate). No need for GraphQL or gRPC
- **버저닝**: url_prefix
- **페이지네이션**: none

---

## 2. 인증

- **방식**: none
- **선택 이유**: Public utility service with no user data. Stateless file conversion only
- **수용 리스크**: Potential abuse via repeated large file uploads, mitigated by file size limit (1MB) and YAML parsing timeout (5s)

---

## 3. 에러 응답

- **포맷**: rfc7807

### 예시

```json
{
  "type": "https://sdwc.dev/errors/validation-failed",
  "title": "Validation Failed",
  "status": 422,
  "detail": "services[0].framework is required but empty",
  "instance": "/api/v1/validate"
}

```

---

## 4. 엔드포인트 상세

### GET /api/v1/template

> Download blank intake_template.yaml

- **인증**: False
- **멱등성**: True
- **동기/비동기**: sync


**응답**

| 필드 | 타입 | 설명 |
|------|------|------|
| file | string | intake_template.yaml file content (application/x-yaml) |

**처리 로직**

1. Return intake_template.yaml as file download

---

### POST /api/v1/validate

> Validate uploaded intake_data.yaml and return detailed errors

- **인증**: False
- **멱등성**: True
- **동기/비동기**: sync

**요청**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| file | string | True | intake_data.yaml file (multipart/form-data) |

**응답**

| 필드 | 타입 | 설명 |
|------|------|------|
| valid | boolean | Whether validation passed |
| errors | json | Array of validation error details (RFC 7807 format) |
| warnings | json | Array of non-blocking warnings |

**처리 로직**

1. Parse and validate uploaded YAML
2. Return validation result with detailed error paths

---

### POST /api/v1/preview

> Preview the file structure and content that would be generated

- **인증**: False
- **멱등성**: True
- **동기/비동기**: sync

**요청**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| file | string | True | intake_data.yaml file (multipart/form-data) |

**응답**

| 필드 | 타입 | 설명 |
|------|------|------|
| file_tree | json | Directory tree of the ZIP that would be generated |
| file_count | integer | Total file count |
| services | json | Service names and their framework selections |

**처리 로직**

1. Validate uploaded YAML
2. Return file tree structure of the ZIP that would be generated

---

### POST /api/v1/generate

> Generate documentation ZIP from intake_data.yaml

- **인증**: False
- **멱등성**: True
- **동기/비동기**: sync

**요청**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| file | string | True | intake_data.yaml file (multipart/form-data) |

**응답**

| 필드 | 타입 | 설명 |
|------|------|------|
| file | string | ZIP file (application/zip) |

**처리 로직**

1. Validate uploaded YAML
2. Render project documentation from templates
3. Package all generated files into ZIP
4. Return ZIP file

---


## 5. 레이트 리밋

- **활성화**: False

<!-- Claude: 수정/추가 시 기존 섹션 구조와 형식을 유지. -->
