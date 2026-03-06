"""YAML parser with safe_load, size limit, and timeout."""

import threading
from typing import Any

import yaml

from sdwc_api.exceptions import YamlParseError
from sdwc_api.schemas.intake import IntakeData

_MAX_SIZE_BYTES = 1_048_576  # 1 MB
_TIMEOUT_SECONDS = 5


def parse_intake_yaml(content: bytes) -> IntakeData:
    """Parse and validate intake YAML content.

    Args:
        content: Raw YAML file bytes.

    Returns:
        Validated IntakeData model.

    Raises:
        YamlParseError: If file exceeds 1MB, YAML is invalid, or parsing times out.
        ValidationError: If data fails Pydantic validation.
    """
    if len(content) > _MAX_SIZE_BYTES:
        raise YamlParseError(f"File size {len(content)} bytes exceeds maximum of {_MAX_SIZE_BYTES} bytes (1MB).")

    result: dict[str, Any] = {}
    error: list[Exception] = []

    def _parse() -> None:
        try:
            data = yaml.safe_load(content.decode("utf-8"))
            result["data"] = data
        except yaml.YAMLError as e:
            error.append(YamlParseError(f"Invalid YAML: {e}"))
        except UnicodeDecodeError as e:
            error.append(YamlParseError(f"Invalid UTF-8 encoding: {e}"))

    thread = threading.Thread(target=_parse, daemon=True)
    thread.start()
    thread.join(timeout=_TIMEOUT_SECONDS)

    if thread.is_alive():
        raise YamlParseError(f"YAML parsing exceeded {_TIMEOUT_SECONDS} second timeout.")

    if error:
        raise error[0]

    data = result.get("data")
    if data is None or not isinstance(data, dict):
        raise YamlParseError("YAML content must be a mapping (object), not a scalar or list.")

    return IntakeData.model_validate(data)
