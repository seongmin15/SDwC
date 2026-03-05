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


class OutputContractError(SdwcError):
    """Raised when rendered output fails output_contract validation."""

    def __init__(self, violations: list[str]) -> None:
        self.violations = violations
        summary = f"{len(violations)} output contract violation(s)"
        detail = "; ".join(violations[:5])
        if len(violations) > 5:
            detail += f" ... and {len(violations) - 5} more"
        super().__init__(f"{summary}: {detail}")
