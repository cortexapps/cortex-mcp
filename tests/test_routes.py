"""Tests for route mapping logic."""
from unittest.mock import Mock

from fastmcp.server.openapi import MCPType

from src.routes.mappers import custom_route_mapper


class TestCustomRouteMapper:
    """Test suite for custom route mapper."""

    def test_route_enabled_as_tool(self, sample_route):
        """Test that routes with x-cortex-mcp-enabled=true become tools."""
        result = custom_route_mapper(sample_route, MCPType.RESOURCE)
        assert result == MCPType.TOOL

    def test_route_explicitly_disabled(self, sample_route):
        """Test that routes with x-cortex-mcp-enabled=false are excluded."""
        sample_route.extensions = {"x-cortex-mcp-enabled": "false"}
        result = custom_route_mapper(sample_route, MCPType.TOOL)
        assert result == MCPType.EXCLUDE

    def test_route_no_extension(self, sample_route):
        """Test that routes without x-cortex-mcp-enabled are excluded."""
        sample_route.extensions = {}
        result = custom_route_mapper(sample_route, MCPType.TOOL)
        assert result == MCPType.EXCLUDE

    def test_different_http_methods(self):
        """Test that all HTTP methods with x-cortex-mcp-enabled=true become tools."""
        methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

        for method in methods:
            route = Mock()
            route.path = "/api/v1/test"
            route.method = method
            route.tags = []
            route.extensions = {"x-cortex-mcp-enabled": "true"}

            result = custom_route_mapper(route, MCPType.RESOURCE)
            assert result == MCPType.TOOL, f"Method {method} should map to TOOL"

    def test_logging_output(self, sample_route, caplog):
        """Test that appropriate debug logs are generated."""
        import logging
        caplog.set_level(logging.DEBUG)

        custom_route_mapper(sample_route, MCPType.RESOURCE)

        assert "Evaluating route: GET /api/v1/resources" in caplog.text
        assert "Tags: ['api', 'resources']" in caplog.text
