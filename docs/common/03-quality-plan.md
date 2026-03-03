# 품질 계획

---

## 1. 테스트 전략

- **접근법**: test_after

### 테스트 레벨

| 레벨 | 커버리지 목표 | 프레임워크 |
|------|-------------|----------|
| unit | 80% | pytest |
| integration |  | pytest |
| unit |  | vitest |
| e2e |  | playwright |

> 테스트 파일 구조, 픽스처/mock 패턴, 실행 명령어 등 상세 규칙은 skills/{service}/testing/ 참조

---

## 2. 보안 요구사항

### 2.1 보안 항목

| 카테고리 | 요구사항 | 구현 접근 |
|---------|---------|----------|
| input_validation | Validate all uploaded YAML against intake schema before processing | Pydantic models for schema validation, PyYAML safe_load for parsing |
| input_validation | Prevent YAML bomb and resource exhaustion attacks | File size limit (1MB), parsing timeout (5s), safe_load only |
| transport_security | HTTPS for all API communication | TLS termination at k3s Traefik ingress |

### 2.2 입력값 검증 전략

Strict validation at /validate endpoint. All requests to /preview and /generate reuse the same validation logic

### 2.3 위협 모델

| 위협 | 완화 방안 |
|------|----------|
| Denial of service via repeated large file uploads | 1MB file size limit, YAML parsing timeout |
| YAML deserialization attack | PyYAML safe_load only (no arbitrary code execution) |


### 2.6 수용한 보안 리스크

| 리스크 | 수용 사유 | 재검토 시점 |
|--------|----------|-----------|
| No authentication -- anyone can use the API | Public utility service with no user data storage. Stateless file conversion only | If usage tracking or rate limiting becomes necessary |

---

## 3. 에러 처리 및 실패 시나리오

### 핵심 플로우별 분석

#### YAML upload and validation

- **정상 흐름**: User uploads valid intake_data.yaml -> server parses and validates -> returns success

- **실패 시나리오**:

| 시나리오 | 가능성 | 영향 | 대응 |
|---------|--------|------|------|
| Malicious YAML (YAML bomb, recursive references) | low | high | safe_load only, 5s parsing timeout, 1MB file size limit, recursive depth limit |
| Invalid YAML syntax | high | low | Return parse error with line number via RFC 7807 |
| Missing required fields | high | low | Return detailed field paths in validation error response |

#### Documentation generation

- **정상 흐름**: Validated intake_data -> Template Engine renders all files -> ZIP packaged and returned

- **실패 시나리오**:

| 시나리오 | 가능성 | 영향 | 대응 |
|---------|--------|------|------|
| Template rendering failure for specific framework/service combination | low | medium | Per-file try-catch, log error, include warning in response. Generate ZIP with remaining files |
| Empty file generated | low | low | Log warning, include file in ZIP with warning. Do not block generation |
| Network timeout during large ZIP generation | low | medium | Set response timeout to 30s. Log generation time for monitoring |


### 전역 에러 처리

- **재시도**: No retries -- stateless request-response. User can retry manually
- **우아한 퇴화**: Partial generation with warnings on non-critical file failures


<!-- Claude: 수정/추가 시 기존 섹션 구조와 형식을 유지. -->
