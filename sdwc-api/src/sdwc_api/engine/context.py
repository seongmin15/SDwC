"""Context composition for Jinja2 rendering.

Transforms validated IntakeData into rendering contexts per generation_rules.md §1-3, §10.

Three context types:
- Global: full intake_data for CLAUDE_BASE.md, doc-templates/common/, skill-templates/common/
- Service: individual service object for doc-templates/{service-type}/
- Skill: service + per_service collaboration for skill-templates/per-framework/{framework}/
"""

from __future__ import annotations

from typing import Any

from sdwc_api.schemas.intake import IntakeData
from sdwc_api.schemas.phase3 import PerServiceCollaboration
from sdwc_api.schemas.phase4_services import (
    BackendApiService,
    DataPipelineService,
    MobileAppService,
    WebUiService,
    WorkerService,
)

ServiceModel = BackendApiService | WebUiService | WorkerService | MobileAppService | DataPipelineService

# Sentinel to mark values for removal during normalization.
_REMOVE = object()


def _normalize_value(value: Any) -> Any:
    """Recursively normalize a single value. Returns _REMOVE if it should be removed."""
    if value is None or value == "":
        return _REMOVE

    if isinstance(value, dict):
        cleaned = {}
        for k, v in value.items():
            result = _normalize_value(v)
            if result is not _REMOVE:
                cleaned[k] = result
        return cleaned if cleaned else _REMOVE

    if isinstance(value, list):
        cleaned_list = []
        for item in value:
            result = _normalize_value(item)
            if result is not _REMOVE:
                cleaned_list.append(result)
        return cleaned_list if cleaned_list else _REMOVE

    # Protect False and 0 — they are explicit values, never removed.
    return value


def normalize(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively remove falsy values per generation_rules.md §10.

    Removes: "", [], {}, None, lists of only empty strings.
    Protects: False, 0 (explicit values).
    Does NOT mutate input; returns a new dict.
    """
    result = {}
    for key, value in data.items():
        normalized = _normalize_value(value)
        if normalized is not _REMOVE:
            result[key] = normalized
    return result


def compose_global_context(intake: IntakeData) -> dict[str, Any]:
    """Compose global rendering context from full intake data.

    Used for: CLAUDE_BASE.md, doc-templates/common/*, skill-templates/common/*
    """
    raw = intake.model_dump(by_alias=True, exclude_none=True)
    return normalize(raw)


def compose_service_context(service: ServiceModel) -> dict[str, Any]:
    """Compose service rendering context from a single service object.

    Used for: doc-templates/{service-type}/*
    Service fields are at root level (no services[i]. prefix).
    """
    raw = service.model_dump(by_alias=True, exclude_none=True)
    return normalize(raw)


def compose_skill_context(service: ServiceModel, per_service: PerServiceCollaboration) -> dict[str, Any]:
    """Compose skill rendering context by merging service + collaboration fields.

    Used for: skill-templates/per-framework/{framework}/*
    Merges so {{ mode }}, {{ test_case_coverage }} are directly accessible.
    """
    service_dict = service.model_dump(by_alias=True, exclude_none=True)
    collab_dict = per_service.model_dump(exclude_none=True)
    collab_dict.pop("service", None)  # remove name-matcher key
    merged = {**service_dict, **collab_dict}
    return normalize(merged)
