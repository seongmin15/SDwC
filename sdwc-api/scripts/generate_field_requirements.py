"""Generate .sdwc/field_requirements.yaml from Pydantic IntakeData model hierarchy.

Introspects the IntakeData model and all nested models recursively to produce
a YAML file documenting every field's requirement level, type, default, and constraints.

Usage:
    cd sdwc-api
    poetry run python scripts/generate_field_requirements.py
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any, Union, get_args, get_origin

import yaml
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

# Ensure src/ is on the path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sdwc_api.schemas.intake import IntakeData
from sdwc_api.schemas.phase4_services import (
    BackendApiService,
    DataPipelineService,
    MobileAppService,
    WebUiService,
    WorkerService,
)

# Service type models for discriminated union introspection
SERVICE_TYPE_MODELS: dict[str, type[BaseModel]] = {
    "backend_api": BackendApiService,
    "web_ui": WebUiService,
    "worker": WorkerService,
    "mobile_app": MobileAppService,
    "data_pipeline": DataPipelineService,
}

# Phase groupings for organizational structure
PHASE_MAP: dict[str, tuple[str, list[str]]] = {
    "phase1_why": (
        "Project Identity",
        ["project", "problem", "motivation", "value_proposition", "project_characteristics"],
    ),
    "phase2_what": (
        "Goals and Scope",
        [
            "goals", "non_goals", "scope", "assumptions", "constraints",
            "timeline", "budget", "glossary",
        ],
    ),
    "phase3_who": (
        "Users and Collaboration",
        ["user_personas", "anti_personas", "stakeholders", "collaboration"],
    ),
    "phase4_how": (
        "Architecture and Services",
        ["architecture", "services"],
    ),
    "phase5_risks": (
        "Critical Flows and Risks",
        ["critical_flows", "global_error_handling", "data_consistency", "security", "risks"],
    ),
    "phase6_quality": (
        "Performance and Observability",
        ["performance", "availability", "observability", "scalability", "external_systems"],
    ),
    "phase7_process": (
        "Process and Version Control",
        ["process", "code_quality", "testing", "version_control"],
    ),
    "phase8_evolution": (
        "Evolution and Operations",
        ["evolution", "rollout", "operations"],
    ),
}

# Models with model_validator conditions
CONDITIONAL_FIELDS: dict[str, dict[str, str]] = {
    "BackendApiService": {
        "endpoints": "required when api_style is 'rest'",
        "graphql": "required when api_style is 'graphql'",
        "grpc": "required when api_style is 'grpc'",
    },
}

# Track visited models to avoid infinite recursion
_visited: set[type] = set()


def _is_union(annotation: Any) -> bool:
    """Check if an annotation is a Union type (typing.Union or types.UnionType)."""
    origin = get_origin(annotation)
    return origin is Union or isinstance(annotation, types.UnionType)


def _type_str(annotation: Any) -> str:
    """Convert a type annotation to a human-readable string."""
    origin = get_origin(annotation)
    args = get_args(annotation)

    if _is_union(annotation):
        # Filter out NoneType for Optional display
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1 and len(args) == 2:
            return f"{_type_str(non_none[0])} | None"
        return " | ".join(_type_str(a) for a in args)

    if origin is list:
        if args:
            return f"list[{_type_str(args[0])}]"
        return "list"

    if origin is dict:
        if args:
            return f"dict[{_type_str(args[0])}, {_type_str(args[1])}]"
        return "dict"

    if hasattr(annotation, "__name__"):
        return annotation.__name__

    return str(annotation)


def _is_pydantic_model(tp: Any) -> bool:
    """Check if a type is a Pydantic BaseModel subclass."""
    try:
        return isinstance(tp, type) and issubclass(tp, BaseModel)
    except TypeError:
        return False


def _get_inner_type(annotation: Any) -> Any:
    """Extract the inner model type from Optional or list wrappers."""
    args = get_args(annotation)

    if _is_union(annotation):
        non_none = [a for a in args if a is not type(None)]
        if non_none:
            return _get_inner_type(non_none[0])

    origin = get_origin(annotation)
    if origin is list and args:
        return args[0]

    return annotation


def _has_default(field_info: FieldInfo) -> bool:
    """Check if a field has an explicit default value (not PydanticUndefined)."""
    return field_info.default is not PydanticUndefined or field_info.default_factory is not None


def _classify_field(
    field_name: str,
    field_info: FieldInfo,
    model_name: str,
) -> str:
    """Classify a field as required, optional, or conditional."""
    # Check conditional map first
    if model_name in CONDITIONAL_FIELDS and field_name in CONDITIONAL_FIELDS[model_name]:
        return "conditional"

    # Check if the annotation includes None (Optional)
    annotation = field_info.annotation
    if annotation is not None and _is_union(annotation):
        args = get_args(annotation)
        if type(None) in args:
            return "optional"

    # Check if field has an explicit default
    if _has_default(field_info):
        return "optional"

    return "required"


def _get_enum_values(tp: Any) -> list[str] | None:
    """Extract enum values if the type is a StrEnum."""
    from enum import StrEnum

    inner = _get_inner_type(tp)
    try:
        if isinstance(inner, type) and issubclass(inner, StrEnum):
            return [e.value for e in inner]
    except TypeError:
        pass
    return None


def _serialize_default(default: Any) -> Any:
    """Convert a default value to a YAML-safe representation."""
    if default is None:
        return None
    if isinstance(default, bool):
        return default
    if isinstance(default, int | float):
        return default
    if isinstance(default, str):
        return default
    return str(default)


def _introspect_model(model: type[BaseModel]) -> dict[str, Any]:
    """Recursively introspect a Pydantic model into a field spec dict."""
    if model in _visited:
        return {"$ref": model.__name__}
    _visited.add(model)

    result: dict[str, Any] = {}
    model_name = model.__name__

    for field_name, field_info in model.model_fields.items():
        annotation = field_info.annotation
        requirement = _classify_field(field_name, field_info, model_name)
        type_display = _type_str(annotation) if annotation else "Any"

        entry: dict[str, Any] = {
            "requirement": requirement,
            "type": type_display,
        }

        # Add default if present (skip PydanticUndefined)
        if field_info.default is not PydanticUndefined:
            entry["default"] = _serialize_default(field_info.default)
        elif (
            requirement == "optional"
            and field_info.default is PydanticUndefined
            and annotation
            and _is_union(annotation)
            and type(None) in get_args(annotation)
        ):
            entry["default"] = None

        # Add conditional description
        if requirement == "conditional":
            entry["condition"] = CONDITIONAL_FIELDS[model_name][field_name]

        # Add enum values
        if annotation:
            enum_vals = _get_enum_values(annotation)
            if enum_vals:
                entry["enum"] = enum_vals

        # Add min_length constraint if present
        if field_info.metadata:
            for meta in field_info.metadata:
                if hasattr(meta, "min_length") and meta.min_length is not None:
                    entry["min_length"] = meta.min_length

        # Recursively introspect nested models
        if annotation:
            inner = _get_inner_type(annotation)
            if _is_pydantic_model(inner):
                entry["children"] = _introspect_model(inner)

        result[field_name] = entry

    _visited.discard(model)
    return result


def generate() -> dict[str, Any]:
    """Generate the full field_requirements structure."""
    output: dict[str, Any] = {
        "version": "1.0",
        "generated_from": "sdwc_api.schemas.intake.IntakeData",
        "phases": {},
    }

    for phase_key, (title, fields) in PHASE_MAP.items():
        phase_entry: dict[str, Any] = {"title": title, "sections": {}}

        for field_name in fields:
            if field_name not in IntakeData.model_fields:
                continue

            field_info = IntakeData.model_fields[field_name]
            annotation = field_info.annotation
            requirement = _classify_field(field_name, field_info, "IntakeData")
            type_display = _type_str(annotation) if annotation else "Any"

            section: dict[str, Any] = {
                "requirement": requirement,
                "type": type_display,
            }

            # Add default info (skip PydanticUndefined)
            if field_info.default is not PydanticUndefined:
                section["default"] = _serialize_default(field_info.default)
            elif (
                requirement == "optional"
                and field_info.default is PydanticUndefined
                and annotation
                and _is_union(annotation)
                and type(None) in get_args(annotation)
            ):
                section["default"] = None

            # Add min_length
            if field_info.metadata:
                for meta in field_info.metadata:
                    if hasattr(meta, "min_length") and meta.min_length is not None:
                        section["min_length"] = meta.min_length

            # Introspect nested model
            if field_name == "services":
                # Special handling for discriminated union
                section["children"] = {}
                for svc_type, svc_model in SERVICE_TYPE_MODELS.items():
                    section["children"][svc_type] = _introspect_model(svc_model)
            elif annotation:
                inner = _get_inner_type(annotation)
                if _is_pydantic_model(inner):
                    section["children"] = _introspect_model(inner)

            phase_entry["sections"][field_name] = section

        output["phases"][phase_key] = phase_entry

    return output


def main() -> None:
    """Generate and write field_requirements.yaml."""
    output_path = Path(__file__).resolve().parent.parent.parent / ".sdwc" / "field_requirements.yaml"

    data = generate()

    # Custom YAML representer for None values
    class NoneRepresenter(yaml.Dumper):
        pass

    def represent_none(dumper: yaml.Dumper, _data: None) -> yaml.ScalarNode:
        return dumper.represent_scalar("tag:yaml.org,2002:null", "null")

    NoneRepresenter.add_representer(type(None), represent_none)

    yaml_content = yaml.dump(
        data,
        Dumper=NoneRepresenter,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    )

    output_path.write_text(yaml_content, encoding="utf-8")
    print(f"Generated: {output_path}")

    # Summary stats
    total_fields = 0
    for phase in data["phases"].values():
        for section in phase["sections"].values():
            total_fields += 1
            if "children" in section:
                total_fields += _count_children(section["children"])

    print(f"Total top-level fields: {len(list(_iter_sections(data)))}")
    print(f"Total fields (including nested): {total_fields}")


def _count_children(children: dict[str, Any]) -> int:
    """Count fields in a children dict recursively."""
    count = len(children)
    for child in children.values():
        if isinstance(child, dict) and "children" in child:
            count += _count_children(child["children"])
    return count


def _iter_sections(data: dict[str, Any]) -> Any:
    """Iterate all top-level sections."""
    for phase in data["phases"].values():
        yield from phase["sections"]


if __name__ == "__main__":
    main()
