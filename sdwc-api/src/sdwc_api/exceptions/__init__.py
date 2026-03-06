"""SDwC domain exceptions with RFC 7807 metadata."""


class SdwcError(Exception):
    """Base exception for sdwc-api domain errors."""

    http_status: int = 500
    error_type: str = "https://sdwc.dev/errors/internal-error"
    title: str = "Internal Error"


class YamlParseError(SdwcError):
    """Raised when YAML parsing or basic validation fails."""

    http_status: int = 422
    error_type: str = "https://sdwc.dev/errors/validation-failed"
    title: str = "Validation Failed"


class PipelineTimeoutError(SdwcError):
    """Raised when the render/generate pipeline exceeds 30s timeout."""

    http_status: int = 408
    error_type: str = "https://sdwc.dev/errors/request-timeout"
    title: str = "Request Timeout"


class RenderingError(SdwcError):
    """Raised when an unexpected rendering error occurs."""

    http_status: int = 500
    error_type: str = "https://sdwc.dev/errors/rendering-failed"
    title: str = "Rendering Failed"


class FrameworkNotFoundError(SdwcError):
    """Raised when a service's framework has no matching skill-templates directory."""

    http_status: int = 422
    error_type: str = "https://sdwc.dev/errors/rendering-failed"
    title: str = "Rendering Failed"

    def __init__(self, framework: str, service_name: str) -> None:
        self.framework = framework
        self.service_name = service_name
        super().__init__(
            f"Framework '{framework}' not found for service '{service_name}'. "
            f"No skill-templates/per-framework/{framework}/ directory."
        )


class OutputContractError(SdwcError):
    """Raised when rendered output fails output_contract validation."""

    http_status: int = 422
    error_type: str = "https://sdwc.dev/errors/output-contract-failed"
    title: str = "Output Contract Failed"

    def __init__(self, violations: list[str]) -> None:
        self.violations = violations
        summary = f"{len(violations)} output contract violation(s)"
        detail = "; ".join(violations[:5])
        if len(violations) > 5:
            detail += f" ... and {len(violations) - 5} more"
        super().__init__(f"{summary}: {detail}")
