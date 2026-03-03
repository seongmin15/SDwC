# 용어집

---

| 용어 | 정의 | 동의어 | 사용 예시 |
|------|------|--------|----------|
| intake_template | Blank YAML survey form that users download and fill in | template | intake_template.yaml (863 lines) |
| intake_data | User-completed YAML file with project-specific values | intake | intake_data.yaml |
| Template Engine | Core server component that combines intake_data with templates to generate output files |  | intake_data + Jinja2 templates -> rendered markdown files |
| skill-templates | Framework-specific coding standard and rule templates (34 frameworks x 4 files + 3 common) | skills | per-framework/fastapi/coding-standards/SKILL.md |
| doc-templates | Jinja2 templates for generating project documentation (18 files) |  | doc-templates/common/00-project-overview.md |
| CLAUDE_BASE | Jinja2 template for generating CLAUDE.md |  | CLAUDE_BASE.md |
| generation_rules | Complete rendering pipeline rules for Template Engine (11 sections) |  | generation_rules.md |
| output_contract | Expected ZIP output specification with validation checklists |  | output_contract.md (291 lines) |

<!-- Claude: 수정/추가 시 기존 섹션 구조와 형식을 유지.
     새 용어는 기존 테이블 형식(용어|정의|동의어|사용 예시)으로 append.
     가나다/알파벳 순 유지. 사용자 승인 후 추가. -->
