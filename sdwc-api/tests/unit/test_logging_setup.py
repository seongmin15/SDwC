"""Tests for structlog configuration."""

import structlog

from sdwc_api.core.logging import setup_logging


class TestSetupLogging:
    def test_configures_structlog(self) -> None:
        setup_logging()
        logger = structlog.get_logger()
        # Logger should be usable after setup
        assert logger is not None

    def test_json_renderer_in_processors(self) -> None:
        setup_logging()
        config = structlog.get_config()
        processor_types = [type(p) for p in config["processors"]]
        assert structlog.processors.JSONRenderer in processor_types

    def test_timestamper_in_processors(self) -> None:
        setup_logging()
        config = structlog.get_config()
        processor_types = [type(p) for p in config["processors"]]
        assert structlog.processors.TimeStamper in processor_types

    def test_contextvars_merge_in_processors(self) -> None:
        setup_logging()
        config = structlog.get_config()
        processors = config["processors"]
        # merge_contextvars is a function, not a class instance
        assert structlog.contextvars.merge_contextvars in processors

    def test_add_log_level_in_processors(self) -> None:
        setup_logging()
        config = structlog.get_config()
        processors = config["processors"]
        assert structlog.processors.add_log_level in processors
