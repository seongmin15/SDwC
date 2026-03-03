# UI 설계

---

## 1. 기술 스택

- **언어**: typescript
- **프레임워크**: react
- **빌드 도구**: vite
- **렌더링**: spa (Single-page file conversion tool. No SEO needed, no multi-page navigation)
- **CSS**: tailwind
- **상태 관리**: zustand

---

## 3. 페이지 상세

### Main

> Single page handling the entire workflow: template download, YAML upload, validation, preview, and ZIP download

**주요 인터랙션:**

- Click template download button to get blank intake_template.yaml
- Upload intake_data.yaml file via drag-and-drop or file picker
- View validation results (success/error details)
- Browse file tree preview of output ZIP
- Download generated ZIP

**연동 API:**

- GET /api/v1/template
- POST /api/v1/validate
- POST /api/v1/preview
- POST /api/v1/generate

**UI 상태:**

- idle -- initial state with template download button and upload area
- uploading -- file being uploaded
- validating -- validation in progress
- validation_error -- validation failed with error details
- previewing -- preview loading
- preview_ready -- file tree displayed, download button enabled
- generating -- ZIP generation in progress
- complete -- ZIP ready for download
- generation_error -- generation failed with error details

**컴포넌트:**

| 컴포넌트 | 역할 |
|---------|------|
| TemplateDownloadButton | Download blank intake_template.yaml |
| FileUploader | Drag-and-drop or file picker for intake_data.yaml upload |
| ValidationResult | Display validation success or detailed error messages |
| FileTreePreview | Display ZIP file structure as collapsible tree |
| GenerateButton | Trigger ZIP generation and download |
| ErrorDisplay | Display generation errors with RFC 7807 details |

---


## 4. 횡단 관심사

- **접근성**: basic
- **반응형**: desktop_first
- **브라우저 지원**: Latest Chrome, Firefox, Safari, Edge

### 디자인 참조

- https://convertio.co (single-page file conversion UX)

<!-- Claude: 수정/추가 시 기존 섹션 구조와 형식을 유지.
     페이지 추가 시 §2 페이지 흐름(mermaid)도 함께 갱신. -->
