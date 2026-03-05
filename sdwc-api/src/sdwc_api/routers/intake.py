"""Intake template and validation endpoints."""

from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse
from pydantic import ValidationError

from sdwc_api.core.config import settings
from sdwc_api.schemas.responses import ValidationErrorItem, ValidationResponse
from sdwc_api.services.yaml_parser import parse_intake_yaml

router = APIRouter(prefix="/api/v1", tags=["intake"])

_ERROR_TYPE = "https://sdwc.dev/errors/validation-failed"
_INSTANCE = "/api/v1/validate"


@router.get("/template")
async def get_template() -> FileResponse:
    """Download blank intake_template.yaml."""
    return FileResponse(
        path=settings.SDWC_RESOURCE_DIR / "intake_template.yaml",
        media_type="application/x-yaml",
        filename="intake_template.yaml",
    )


@router.post("/validate", response_model=ValidationResponse)
async def validate_intake(file: UploadFile) -> ValidationResponse:
    """Validate uploaded intake YAML and return detailed errors."""
    content = await file.read()

    try:
        parse_intake_yaml(content)
    except (ValueError, TimeoutError) as exc:
        return ValidationResponse(
            valid=False,
            errors=[
                ValidationErrorItem(
                    type=_ERROR_TYPE,
                    title="Validation Failed",
                    status=422,
                    detail=str(exc),
                    instance=_INSTANCE,
                ),
            ],
            warnings=[],
        )
    except ValidationError as exc:
        errors = [
            ValidationErrorItem(
                type=_ERROR_TYPE,
                title="Validation Failed",
                status=422,
                detail=f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}",
                instance=_INSTANCE,
            )
            for e in exc.errors()
        ]
        return ValidationResponse(valid=False, errors=errors, warnings=[])

    return ValidationResponse(valid=True, errors=[], warnings=[])
