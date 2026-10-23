"""Tests for component customization."""
from unittest.mock import Mock

from fastmcp.server.providers.openapi import (
    OpenAPIResource,
    OpenAPIResourceTemplate,
    OpenAPITool,
)

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


class TestToolAnnotations:
    """Hints that let clients approve read tools apart from write tools."""

    @staticmethod
    def _tool(route):
        tool = Mock(spec=OpenAPITool)
        tool.description = ""
        tool.tags = set()
        customize_components(route, tool)
        return tool

    def test_get_is_read_only(self, sample_route):
        assert self._tool(sample_route).annotations.read_only_hint is True

    def test_other_methods_default_to_destructive(self, sample_route):
        sample_route.method = "POST"

        annotations = self._tool(sample_route).annotations

        assert annotations.read_only_hint is False
        assert annotations.destructive_hint is True
        assert annotations.idempotent_hint is False

    def test_put_is_idempotent(self, sample_route):
        sample_route.method = "PUT"

        assert self._tool(sample_route).annotations.idempotent_hint is True

    def test_access_extension_marks_a_post_read_only(self, sample_route):
        sample_route.method = "POST"
        sample_route.extensions = {"x-cortex-mcp-access": "read"}

        assert self._tool(sample_route).annotations.read_only_hint is True

    def test_access_extension_marks_a_write_additive(self, sample_route):
        sample_route.method = "POST"
        sample_route.extensions = {"x-cortex-mcp-access": "additive"}

        annotations = self._tool(sample_route).annotations

        assert annotations.read_only_hint is False
        assert annotations.destructive_hint is False

    def test_title_is_the_summary(self, sample_route):
        assert self._tool(sample_route).title == "List resources"
