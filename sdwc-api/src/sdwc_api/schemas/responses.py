"""API response models."""

from typing import Any

from pydantic import BaseModel


class ValidationErrorItem(BaseModel):
    """RFC 7807 problem detail for a single validation error."""

    type: str
    title: str
    status: int
    detail: str
    instance: str


class ValidationResponse(BaseModel):
    """Response body for POST /api/v1/validate."""

    valid: bool
    errors: list[ValidationErrorItem]
    warnings: list[ValidationErrorItem]


class ServiceInfo(BaseModel):
    """Service summary for preview response."""

    name: str
    type: str
    framework: str


class PreviewResponse(BaseModel):
    """Response body for POST /api/v1/preview."""

    file_tree: dict[str, Any]
    file_count: int
    services: list[ServiceInfo]
