"""SDwC domain exceptions."""


class SdwcError(Exception):
    """Base exception for sdwc-api domain errors."""


class FrameworkNotFoundError(SdwcError):
    """Raised when a service's framework has no matching skill-templates directory."""

    def __init__(self, framework: str, service_name: str) -> None:
        self.framework = framework
        self.service_name = service_name
        super().__init__(
            f"Framework '{framework}' not found for service '{service_name}'. "
            f"No skill-templates/per-framework/{framework}/ directory."
        )
