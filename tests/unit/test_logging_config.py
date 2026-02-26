"""Unit tests for src.logging_config (setup_logging, get_logger)."""
import logging
from unittest.mock import patch

from src.logging_config import setup_logging, get_logger

class TestGetLogger:

    def test_returns_logger_instance(self):
        lg = get_logger("test-unit")
        assert isinstance(lg, logging.Logger)

    def test_logger_has_correct_name(self):
        lg = get_logger("my-module")
        assert lg.name == "my-module"

    def test_same_name_returns_same_logger(self):
        a = get_logger("shared")
        b = get_logger("shared")
        assert a is b


class TestSetupLogging:

    @patch("src.logging_config.logging.basicConfig")
    def test_sets_root_logger_level(self, mock_basic_config):
        setup_logging(level=logging.DEBUG)
        mock_basic_config.assert_called_once()
        _, kwargs = mock_basic_config.call_args
        assert kwargs["level"] == logging.DEBUG

    @patch("src.logging_config.logging.basicConfig")
    def test_default_level_is_info(self, mock_basic_config):
        setup_logging()
        _, kwargs = mock_basic_config.call_args
        assert kwargs["level"] == logging.INFO

    @patch("src.logging_config.logging.basicConfig")
    def test_default_format_contains_levelname(self, mock_basic_config):
        """Default format string should include standard log record fields."""
        setup_logging()
        _, kwargs = mock_basic_config.call_args
        assert "%(levelname)s" in kwargs["format"]
        assert "%(name)s" in kwargs["format"]

    @patch("src.logging_config.logging.basicConfig")
    def test_custom_format_is_passed_to_basic_config(self, mock_basic_config):
        setup_logging(format_string="%(message)s")
        _, kwargs = mock_basic_config.call_args
        assert kwargs["format"] == "%(message)s"

