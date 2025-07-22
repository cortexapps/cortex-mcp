"""Tests for component customization."""
from unittest.mock import Mock

from fastmcp.server.openapi import OpenAPIResource, OpenAPIResourceTemplate, OpenAPITool

from src.components.customizers import customize_components


class TestCustomizeComponents:
    """Test suite for component customization."""

    def test_custom_description_override(self, sample_route):
        """Test that x-cortex-mcp-description overrides default description."""
        sample_route.extensions = {"x-cortex-mcp-description": "Custom description"}

        component = Mock()
        component.description = "Original description"
        component.tags = set()

        customize_components(sample_route, component)

        assert component.description == "Custom description"

    def test_tags_added(self, sample_route):
        """Test that appropriate tags are added to components."""
        component = Mock()
        component.tags = set()
        component.description = ""

        customize_components(sample_route, component)

        assert "cortex-api" in component.tags
        assert "openapi" in component.tags
        assert "api" in component.tags
        assert "resources" in component.tags

    def test_tool_formatting(self, sample_route):
        """Test OpenAPITool description formatting."""
        sample_route.method = "POST"
        sample_route.path = "/api/v1/users"

        tool = Mock(spec=OpenAPITool)
        tool.description = ""
        tool.tags = set()

        customize_components(sample_route, tool)

        assert tool.description.startswith("Create users")

    def test_resource_formatting(self, sample_route):
        """Test OpenAPIResource description formatting."""
        sample_route.path = "/api/v1/products"

        resource = Mock(spec=OpenAPIResource)
        resource.description = ""
        resource.tags = set()

        customize_components(sample_route, resource)

        assert "Retrieve a list of products" in resource.description

    def test_resource_template_formatting(self, sample_route):
        """Test OpenAPIResourceTemplate description formatting."""
        sample_route.path = "/api/v1/orders/{id}"

        template = Mock(spec=OpenAPIResourceTemplate)
        template.description = ""
        template.tags = set()

        customize_components(sample_route, template)

        assert "specific order" in template.description

    def test_preserve_original_description(self, sample_route):
        """Test that original descriptions are preserved when no custom description."""
        original = "This is the original description"

        tool = Mock(spec=OpenAPITool)
        tool.description = original
        tool.tags = set()

        customize_components(sample_route, tool)

        assert original in tool.description
        assert tool.description != original
