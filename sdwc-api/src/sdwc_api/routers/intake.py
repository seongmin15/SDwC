"""Intake template, validation, preview, and generation endpoints."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
from typing import Any

from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import ValidationError

from sdwc_api.core.config import settings
from sdwc_api.engine.packager import build_zip
from sdwc_api.engine.renderer import render_all
from sdwc_api.engine.validator import validate_or_raise
from sdwc_api.exceptions import PipelineTimeoutError, YamlParseError
from sdwc_api.schemas.responses import (
    PreviewResponse,
    ServiceInfo,
    ValidationErrorItem,
    ValidationResponse,
)
from sdwc_api.services.yaml_parser import parse_intake_yaml

router = APIRouter(prefix="/api/v1", tags=["intake"])

_PIPELINE_TIMEOUT = 30.0


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _validation_error_items(
    exc: ValidationError,
    instance: str,
) -> list[ValidationErrorItem]:
    """Convert Pydantic ValidationError to RFC 7807 items."""
    return [
        ValidationErrorItem(
            type="https://sdwc.dev/errors/validation-failed",
            title="Validation Failed",
            status=422,
            detail=f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}",
            instance=instance,
        )
        for e in exc.errors()
    ]


def _build_file_tree(paths: Iterable[str]) -> dict[str, Any]:
    """Build a nested dict tree from flat output paths."""
    tree: dict[str, Any] = {}
    for path in sorted(paths):
        parts = path.split("/")
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = {}
    return tree


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/template")
async def get_template() -> FileResponse:
    """Download blank intake_template.yaml."""
    return FileResponse(
        path=settings.SDWC_RESOURCE_DIR / "intake_template.yaml",
        media_type="application/x-yaml",
        filename="intake_template.yaml",
    )


@router.get("/field-requirements")
async def get_field_requirements() -> FileResponse:
    """Download field_requirements.yaml."""
    return FileResponse(
        path=settings.SDWC_RESOURCE_DIR / "field_requirements.yaml",
        media_type="application/x-yaml",
        filename="field_requirements.yaml",
    )


@router.post("/validate", response_model=ValidationResponse)
async def validate_intake(file: UploadFile) -> ValidationResponse:
    """Validate uploaded intake YAML and return detailed errors."""
    content = await file.read()
    instance = "/api/v1/validate"

    try:
        parse_intake_yaml(content)
    except YamlParseError as exc:
        return ValidationResponse(
            valid=False,
            errors=[
                ValidationErrorItem(
                    type="https://sdwc.dev/errors/validation-failed",
                    title="Validation Failed",
                    status=422,
                    detail=str(exc),
                    instance=instance,
                ),
            ],
            warnings=[],
        )
    except ValidationError as exc:
        return ValidationResponse(
            valid=False,
            errors=_validation_error_items(exc, instance),
            warnings=[],
        )

    return ValidationResponse(valid=True, errors=[], warnings=[])


@router.post("/preview", response_model=PreviewResponse)
async def preview_output(file: UploadFile) -> PreviewResponse:
    """Preview the file structure that would be generated."""
    content = await file.read()
    intake = parse_intake_yaml(content)

    try:
        rendered = await asyncio.wait_for(
            asyncio.to_thread(render_all, intake, settings.SDWC_RESOURCE_DIR),
            timeout=_PIPELINE_TIMEOUT,
        )
    except TimeoutError:
        raise PipelineTimeoutError(
            f"Template rendering exceeded {_PIPELINE_TIMEOUT:.0f}s timeout"
        ) from None

    services = [ServiceInfo(name=svc.name, type=svc.type, framework=str(svc.framework)) for svc in intake.services]

    return PreviewResponse(
        file_tree=_build_file_tree(rendered.keys()),
        file_count=len(rendered),
        services=services,
    )


@router.post("/generate", response_model=None)
async def generate_output(file: UploadFile) -> StreamingResponse:
    """Generate documentation ZIP from intake YAML."""
    content = await file.read()
    intake = parse_intake_yaml(content)

    try:

        def _pipeline() -> dict[str, str]:
            rendered = render_all(intake, settings.SDWC_RESOURCE_DIR)
            validate_or_raise(rendered, intake)
            return rendered

        rendered = await asyncio.wait_for(
            asyncio.to_thread(_pipeline),
            timeout=_PIPELINE_TIMEOUT,
        )
    except TimeoutError:
        raise PipelineTimeoutError(
            f"Generation pipeline exceeded {_PIPELINE_TIMEOUT:.0f}s timeout"
        ) from None

    zip_buf = build_zip(rendered, intake, settings.SDWC_RESOURCE_DIR)
    filename = f"{intake.project.name}.zip"

    return StreamingResponse(
        zip_buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
