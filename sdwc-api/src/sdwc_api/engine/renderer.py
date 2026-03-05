"""Jinja2 rendering pipeline for SDwC template engine.

Renders .sdwc/ templates into output files per generation_rules.md §4-6, §8-9.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import jinja2

from sdwc_api.engine.context import (
    ServiceModel,
    compose_global_context,
    compose_service_context,
    compose_skill_context,
)
from sdwc_api.exceptions import FrameworkNotFoundError
from sdwc_api.schemas.intake import IntakeData
from sdwc_api.schemas.phase3 import PerServiceCollaboration


def _make_adr_seq() -> Callable[[], int]:
    """Create a fresh ADR sequential numbering closure.

    Each call increments and returns the next number, starting at 1.
    A new closure is created per render_all call so numbering resets.
    """
    counter = [0]

    def _next() -> int:
        counter[0] += 1
        return counter[0]

    return _next


def create_jinja_env(template_dir: Path) -> jinja2.Environment:
    """Create a Jinja2 environment configured for Markdown rendering.

    Args:
        template_dir: Root directory containing .sdwc/ templates.
    """
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        autoescape=False,
        undefined=jinja2.Undefined,
    )


def _discover_templates(template_dir: Path, subdir: str) -> list[str]:
    """Walk a subdirectory under template_dir and collect *.md files.

    Returns sorted paths relative to template_dir using forward slashes.
    Returns empty list if the directory does not exist.
    """
    target = template_dir / subdir
    if not target.is_dir():
        return []
    paths = [p.relative_to(template_dir).as_posix() for p in sorted(target.rglob("*.md")) if p.is_file()]
    return paths


def _map_output_path(template_rel_path: str, service_name: str | None = None) -> str:
    """Map a template-relative path to its output path per §9.

    Args:
        template_rel_path: Path relative to template_dir (forward slashes).
        service_name: Service name for service-specific mappings.
    """
    if template_rel_path == "CLAUDE_BASE.md":
        return "CLAUDE.md"

    if template_rel_path.startswith("doc-templates/common/"):
        return template_rel_path.replace("doc-templates/common/", "docs/common/", 1)

    # doc-templates/{service-type}/ → docs/{service-name}/
    if template_rel_path.startswith("doc-templates/") and service_name is not None:
        # Extract the filename after doc-templates/{service-type}/
        parts = template_rel_path.split("/", 2)  # ['doc-templates', '{type}', '{file}']
        if len(parts) == 3:
            return f"docs/{service_name}/{parts[2]}"

    if template_rel_path.startswith("skill-templates/common/"):
        return template_rel_path.replace("skill-templates/common/", "skills/common/", 1)

    # skill-templates/per-framework/{fw}/ → skills/{service-name}/
    if template_rel_path.startswith("skill-templates/per-framework/") and service_name is not None:
        # Extract after skill-templates/per-framework/{fw}/
        parts = template_rel_path.split("/", 3)  # ['skill-templates', 'per-framework', '{fw}', '{rest}']
        if len(parts) == 4:
            return f"skills/{service_name}/{parts[3]}"

    return template_rel_path


def _render_template(env: jinja2.Environment, template_path: str, context: dict[str, Any]) -> str:
    """Render a single template with the given context."""
    return env.get_template(template_path).render(**context)


def _find_per_service(intake: IntakeData, service_name: str) -> PerServiceCollaboration:
    """Look up PerServiceCollaboration by service name.

    IntakeData validation guarantees a 1:1 match between services and per_service.
    """
    for ps in intake.collaboration.per_service:
        if ps.service == service_name:
            return ps
    # Should never reach here due to IntakeData model_validator
    msg = f"No per_service entry for '{service_name}'"
    raise ValueError(msg)


def _get_service_type(service: ServiceModel) -> str:
    """Extract the type string from a service model."""
    return service.type


def render_all(intake: IntakeData, template_dir: Path) -> dict[str, str]:
    """Render all templates and return {output_path: rendered_content}.

    Orchestrates the full rendering pipeline:
    1. CLAUDE_BASE.md → CLAUDE.md (global context)
    2. doc-templates/common/ → docs/common/ (global context)
    3. skill-templates/common/ → skills/common/ (global context)
    4. Per service: doc-templates/{type}/ and skill-templates/per-framework/{fw}/

    Args:
        intake: Validated intake data.
        template_dir: Root directory containing templates (.sdwc/ root).

    Returns:
        Dict mapping output paths to rendered content.

    Raises:
        FrameworkNotFoundError: If a service's framework has no skill-templates directory.
    """
    env = create_jinja_env(template_dir)
    env.globals["adr_seq"] = _make_adr_seq()

    global_ctx = compose_global_context(intake)
    output: dict[str, str] = {}

    # Phase 1: CLAUDE_BASE.md → CLAUDE.md
    claude_base = "CLAUDE_BASE.md"
    if (template_dir / claude_base).is_file():
        rendered = _render_template(env, claude_base, global_ctx)
        output[_map_output_path(claude_base)] = rendered

    # Phase 2: doc-templates/common/ → docs/common/
    for tpl in _discover_templates(template_dir, "doc-templates/common"):
        rendered = _render_template(env, tpl, global_ctx)
        output[_map_output_path(tpl)] = rendered

    # Phase 3: skill-templates/common/ → skills/common/
    for tpl in _discover_templates(template_dir, "skill-templates/common"):
        rendered = _render_template(env, tpl, global_ctx)
        output[_map_output_path(tpl)] = rendered

    # Phase 4: Per service
    for service in intake.services:
        svc_name = service.name
        svc_type = _get_service_type(service)
        per_svc = _find_per_service(intake, svc_name)

        # Service docs: doc-templates/{service-type}/ → docs/{service-name}/
        svc_ctx = compose_service_context(service)
        for tpl in _discover_templates(template_dir, f"doc-templates/{svc_type}"):
            rendered = _render_template(env, tpl, svc_ctx)
            output[_map_output_path(tpl, svc_name)] = rendered

        # Framework skills: skill-templates/per-framework/{fw}/ → skills/{service-name}/
        fw = service.framework
        fw_dir = f"skill-templates/per-framework/{fw}"
        if not (template_dir / fw_dir).is_dir():
            raise FrameworkNotFoundError(framework=str(fw), service_name=svc_name)

        skill_ctx = compose_skill_context(service, per_svc)
        for tpl in _discover_templates(template_dir, fw_dir):
            rendered = _render_template(env, tpl, skill_ctx)
            output[_map_output_path(tpl, svc_name)] = rendered

    return output
