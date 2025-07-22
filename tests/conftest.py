"""Pytest configuration and shared fixtures."""
import os
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        "CORTEX_API_TOKEN": "test-token-123",
        "CORTEX_API_BASE_URL": "https://test.api.com",
        "MCP_HOST": "localhost",
        "MCP_PORT": "8080",
        "MCP_TRANSPORT": "stdio",
        "OPENAPI_SPEC_PATH": "/tmp/test-spec.json",
        "LOG_LEVEL": "DEBUG",
        "DEBUG": "true"
    }):
        yield


@pytest.fixture
def sample_route():
    """Create a sample HTTPRoute for testing."""
    route = Mock()
    route.path = "/api/v1/resources"
    route.method = "GET"
    route.tags = ["api", "resources"]
    route.extensions = {"x-cortex-mcp-enabled": "true"}
    return route


@pytest.fixture
def sample_openapi_spec():
    """Create a sample OpenAPI spec for testing."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0"
        },
        "paths": {
            "/api/v1/resources": {
                "get": {
                    "tags": ["resources"],
                    "x-cortex-mcp-enabled": "true",
                    "summary": "List resources"
                }
            }
        }
    }
