"""API response models."""

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
