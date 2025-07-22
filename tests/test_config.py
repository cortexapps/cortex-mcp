"""Tests for configuration module."""
from unittest.mock import patch

import pytest

from src.config import Config


class TestConfig:
    """Test suite for Config class."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        assert Config.CORTEX_API_BASE_URL == "https://api.getcortexapp.com"
        assert Config.HOST == "0.0.0.0"
        assert Config.PORT == 8000
        assert Config.TRANSPORT == "streamable-http"
        assert Config.LOG_LEVEL == "INFO"
        assert Config.APP_NAME == "Cortex MCP Server"

    def test_env_var_override(self, mock_env_vars):
        """Test that environment variables override defaults."""
        from importlib import reload

        import src.config
        reload(src.config)

        assert src.config.Config.CORTEX_API_TOKEN == "test-token-123"
        assert src.config.Config.HOST == "localhost"
        assert src.config.Config.PORT == 8080
        assert src.config.Config.LOG_LEVEL == "DEBUG"
        assert src.config.Config.DEBUG is True

    def test_validate_missing_openapi_spec(self):
        """Test validation fails when OpenAPI spec is missing."""
        with patch.object(Config, 'OPENAPI_SPEC_PATH', '/nonexistent/path.json'):
            with pytest.raises(ValueError, match="OpenAPI spec file not found"):
                Config.validate()

    def test_validate_success(self, tmp_path):
        """Test validation succeeds with valid configuration."""
        spec_file = tmp_path / "openapi.json"
        spec_file.write_text("{}")

        with patch.object(Config, 'OPENAPI_SPEC_PATH', str(spec_file)):
            Config.validate()

    def test_get_masked_token_not_set(self):
        """Test token masking when token is not set."""
        with patch.object(Config, 'CORTEX_API_TOKEN', ''):
            assert Config.get_masked_token() == "NOT_SET"

    def test_get_masked_token_short(self):
        """Test token masking for short tokens."""
        with patch.object(Config, 'CORTEX_API_TOKEN', 'short'):
            assert Config.get_masked_token() == "***"

    def test_get_masked_token_normal(self):
        """Test token masking for normal tokens."""
        with patch.object(Config, 'CORTEX_API_TOKEN', 'abcdefghijklmnop'):
            masked = Config.get_masked_token()
            assert masked == "abcd...mnop"
            assert len(masked) == 11
