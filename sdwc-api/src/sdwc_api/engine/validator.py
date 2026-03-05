"""Output contract validation for rendered SDwC templates.

Validates rendered dict against output_contract.md:
- Structure checks S-2 through S-9
- Content checks C-1 through C-7
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from sdwc_api.engine.context import ServiceModel
from sdwc_api.engine.postprocess import (
    _is_claude_managed,
    rule_merge_consecutive_dividers,
    rule_remove_empty_sections,
    rule_remove_empty_tables,
    rule_remove_trailing_whitespace,
)
from sdwc_api.exceptions import OutputContractError
from sdwc_api.schemas.intake import IntakeData

_COMMON_DOCS: frozenset[str] = frozenset(
    {
        "docs/common/00-project-overview.md",
        "docs/common/01-requirements.md",
        "docs/common/02-architecture-decisions.md",
        "docs/common/03-quality-plan.md",
        "docs/common/04-infrastructure.md",
        "docs/common/05-roadmap.md",
        "docs/common/06-glossary.md",
        "docs/common/07-workplan.md",
        "docs/common/09-working-log.md",
        "docs/common/10-changelog.md",
        "docs/common/11-troubleshooting.md",
        "docs/common/12-runbook.md",
    }
)

_COMMON_SKILLS: frozenset[str] = frozenset(
    {
        "skills/common/git/SKILL.md",
        "skills/common/observability/SKILL.md",
        "skills/common/code-comments/SKILL.md",
    }
)

_SERVICE_DOCS: dict[str, list[str]] = {
    "backend_api": ["20-data-design.md", "21-api-contract.md"],
    "web_ui": ["30-ui-design.md"],
    "worker": ["40-worker-design.md"],
    "mobile_app": ["50-mobile-design.md"],
    "data_pipeline": ["60-pipeline-design.md"],
}

_SERVICE_SKILL_FOLDERS: frozenset[str] = frozenset(
    {
        "coding-standards",
        "testing",
        "framework",
        "deployment",
    }
)


# --- Structure checks ---


def _check_s2(rendered: dict[str, str]) -> list[str]:
    """S-2: CLAUDE.md must exist."""
    if "CLAUDE.md" not in rendered:
        return ["S-2: CLAUDE.md not found in output"]
    return []


def _check_s3(rendered: dict[str, str]) -> list[str]:
    """S-3: docs/common/ must have exactly 12 specific files."""
    violations: list[str] = []
    actual = {k for k in rendered if k.startswith("docs/common/")}
    missing = _COMMON_DOCS - actual
    extra = actual - _COMMON_DOCS
    if missing:
        violations.append(f"S-3: missing docs/common/ files: {sorted(missing)}")
    if extra:
        violations.append(f"S-3: unexpected docs/common/ files: {sorted(extra)}")
    return violations


def _check_s4(rendered: dict[str, str]) -> list[str]:
    """S-4: skills/common/ must have exactly 3 SKILL.md files."""
    violations: list[str] = []
    actual = {k for k in rendered if k.startswith("skills/common/")}
    missing = _COMMON_SKILLS - actual
    extra = actual - _COMMON_SKILLS
    if missing:
        violations.append(f"S-4: missing skills/common/ files: {sorted(missing)}")
    if extra:
        violations.append(f"S-4: unexpected skills/common/ files: {sorted(extra)}")
    return violations


def _check_s5(rendered: dict[str, str], services: Sequence[ServiceModel]) -> list[str]:
    """S-5: For each service, both docs/{name}/ and skills/{name}/ must exist."""
    violations: list[str] = []
    for svc in services:
        name = svc.name
        has_docs = any(k.startswith(f"docs/{name}/") for k in rendered)
        has_skills = any(k.startswith(f"skills/{name}/") for k in rendered)
        if not has_docs:
            violations.append(f"S-5: no docs/{name}/ files found")
        if not has_skills:
            violations.append(f"S-5: no skills/{name}/ files found")
    return violations


def _check_s6(rendered: dict[str, str], services: Sequence[ServiceModel]) -> list[str]:
    """S-6: Service docs must match type-specific file expectations."""
    violations: list[str] = []
    for svc in services:
        name = svc.name
        svc_type = svc.type
        expected_filenames = _SERVICE_DOCS.get(svc_type, [])
        expected_paths = {f"docs/{name}/{f}" for f in expected_filenames}
        actual = {k for k in rendered if k.startswith(f"docs/{name}/")}
        missing = expected_paths - actual
        extra = actual - expected_paths
        if missing:
            violations.append(f"S-6: service '{name}' missing doc files: {sorted(missing)}")
        if extra:
            violations.append(f"S-6: service '{name}' has unexpected doc files: {sorted(extra)}")
    return violations


def _check_s7(rendered: dict[str, str], services: Sequence[ServiceModel]) -> list[str]:
    """S-7: Each service must have exactly 4 skill folders."""
    violations: list[str] = []
    for svc in services:
        name = svc.name
        expected = {f"skills/{name}/{folder}/SKILL.md" for folder in _SERVICE_SKILL_FOLDERS}
        actual = {k for k in rendered if k.startswith(f"skills/{name}/")}
        missing = expected - actual
        extra = actual - expected
        if missing:
            violations.append(f"S-7: service '{name}' missing skill files: {sorted(missing)}")
        if extra:
            violations.append(f"S-7: service '{name}' has unexpected skill files: {sorted(extra)}")
    return violations


def _check_s8(rendered: dict[str, str], services: Sequence[ServiceModel]) -> list[str]:
    """S-8: Total file count must match formula: 16 + sum(docs_count) + 4*N."""
    n = len(services)
    docs_sum: int = 0
    for svc in services:
        docs_sum += len(_SERVICE_DOCS.get(svc.type, []))
    expected = 16 + docs_sum + 4 * n
    actual = len(rendered)
    if actual != expected:
        return [f"S-8: expected {expected} files, got {actual}"]
    return []


def _check_s9(rendered: dict[str, str]) -> list[str]:
    """S-9: No empty files (all values must have content)."""
    violations: list[str] = []
    for path, content in rendered.items():
        if len(content) == 0:
            violations.append(f"S-9: empty file: {path}")
    return violations


# --- Content checks ---


def _check_c1(rendered: dict[str, str]) -> list[str]:
    """C-1: No unsubstituted Jinja2 {{ or }} in rendered content."""
    violations: list[str] = []
    for path, content in rendered.items():
        if "{{" in content or "}}" in content:
            violations.append(f"C-1: unsubstituted Jinja2 found in {path}")
    return violations


def _check_c2(rendered: dict[str, str]) -> list[str]:
    """C-2: ADR numbers in 02-architecture-decisions.md must be consecutive."""
    adr_path = "docs/common/02-architecture-decisions.md"
    if adr_path not in rendered:
        return []
    content = rendered[adr_path]
    numbers = [int(m) for m in re.findall(r"ADR-(\d+)", content)]
    if not numbers:
        return []
    expected = list(range(1, len(numbers) + 1))
    if numbers != expected:
        return [f"C-2: ADR numbers are not consecutive: {numbers}"]
    return []


def _check_c3(rendered: dict[str, str]) -> list[str]:
    """C-3: No empty Mermaid code blocks."""
    violations: list[str] = []
    pattern = re.compile(r"```mermaid\s*```", re.DOTALL)
    for path, content in rendered.items():
        if pattern.search(content):
            violations.append(f"C-3: empty mermaid block in {path}")
    return violations


def _check_c4(rendered: dict[str, str]) -> list[str]:
    """C-4: No empty tables (header+separator only, no data rows)."""
    violations: list[str] = []
    for path, content in rendered.items():
        if rule_remove_empty_tables(content) != content:
            violations.append(f"C-4: empty table found in {path}")
    return violations


def _check_c5(rendered: dict[str, str]) -> list[str]:
    """C-5: No empty sections (except Claude-managed files)."""
    violations: list[str] = []
    for path, content in rendered.items():
        if _is_claude_managed(path):
            continue
        if rule_remove_empty_sections(content) != content:
            violations.append(f"C-5: empty section found in {path}")
    return violations


def _check_c6(rendered: dict[str, str]) -> list[str]:
    """C-6: No consecutive --- dividers."""
    violations: list[str] = []
    for path, content in rendered.items():
        if rule_merge_consecutive_dividers(content) != content:
            violations.append(f"C-6: consecutive dividers found in {path}")
    return violations


def _check_c7(rendered: dict[str, str]) -> list[str]:
    """C-7: No trailing whitespace."""
    violations: list[str] = []
    for path, content in rendered.items():
        if rule_remove_trailing_whitespace(content) != content:
            violations.append(f"C-7: trailing whitespace found in {path}")
    return violations


# --- Orchestrators ---


def validate_output(rendered: dict[str, str], intake: IntakeData) -> list[str]:
    """Validate rendered output dict against output_contract.md.

    Args:
        rendered: Output from render_all() — {output_path: content}.
        intake: Original intake data (needed for service names/types).

    Returns:
        Empty list if valid. List of violation strings if invalid.
        Each string is prefixed with the check ID (e.g. "S-2: ...").
    """
    services = intake.services
    violations: list[str] = []
    violations.extend(_check_s2(rendered))
    violations.extend(_check_s3(rendered))
    violations.extend(_check_s4(rendered))
    violations.extend(_check_s5(rendered, services))
    violations.extend(_check_s6(rendered, services))
    violations.extend(_check_s7(rendered, services))
    violations.extend(_check_s8(rendered, services))
    violations.extend(_check_s9(rendered))
    violations.extend(_check_c1(rendered))
    violations.extend(_check_c2(rendered))
    violations.extend(_check_c3(rendered))
    violations.extend(_check_c4(rendered))
    violations.extend(_check_c5(rendered))
    violations.extend(_check_c6(rendered))
    violations.extend(_check_c7(rendered))
    return violations


def validate_or_raise(rendered: dict[str, str], intake: IntakeData) -> None:
    """Validate and raise OutputContractError if violations found.

    Args:
        rendered: Output from render_all().
        intake: Original intake data.

    Raises:
        OutputContractError: If any validation check fails.
    """
    violations = validate_output(rendered, intake)
    if violations:
        raise OutputContractError(violations)
