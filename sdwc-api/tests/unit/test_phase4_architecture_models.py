"""Tests for Phase 4 models: Architecture."""

import pytest
from pydantic import ValidationError

from sdwc_api.schemas.phase4_architecture import (
    Architecture,
    PatternAlternative,
)


class TestArchitecture:
    def test_create_with_required_fields_succeeds(self) -> None:
        a = Architecture(
            pattern="monolith",
            pattern_rationale="Simple for MVP",
            pattern_alternatives=[
                PatternAlternative(
                    pattern="microservices",
                    pros="Scalability",
                    cons="Complexity",
                    rejection_reason="Overkill for MVP",
                ),
            ],
        )
        assert a.pattern == "monolith"
        assert a.internal_style is None
        assert a.principles is None

    def test_create_with_all_fields_succeeds(self) -> None:
        a = Architecture(
            pattern="modular_monolith",
            pattern_rationale="Balance",
            pattern_alternatives=[
                PatternAlternative(
                    pattern="monolith",
                    pros="Simple",
                    cons="Coupling",
                    rejection_reason="Too coupled",
                ),
            ],
            internal_style="layered",
            internal_style_rationale="Team familiarity",
            principles=["DRY", "KISS"],
        )
        assert a.internal_style == "layered"
        assert len(a.principles) == 2

    def test_invalid_pattern_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Architecture(
                pattern="serverless",
                pattern_rationale="x",
                pattern_alternatives=[
                    PatternAlternative(pattern="x", pros="x", cons="x", rejection_reason="x"),
                ],
            )
        assert "pattern" in str(exc_info.value)

    def test_invalid_internal_style_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Architecture(
                pattern="monolith",
                pattern_rationale="x",
                pattern_alternatives=[
                    PatternAlternative(pattern="x", pros="x", cons="x", rejection_reason="x"),
                ],
                internal_style="onion",
            )
        assert "internal_style" in str(exc_info.value)

    def test_empty_pattern_alternatives_raises_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Architecture(
                pattern="monolith",
                pattern_rationale="x",
                pattern_alternatives=[],
            )
        assert "pattern_alternatives" in str(exc_info.value)
