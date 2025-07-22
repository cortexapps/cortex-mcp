"""Component customization for MCP server."""

from fastmcp.server.openapi import (
    HTTPRoute,
    OpenAPIResource,
    OpenAPIResourceTemplate,
    OpenAPITool,
)

from ..utils.logging import get_logger

logger = get_logger(__name__)

ComponentType = OpenAPITool | OpenAPIResource | OpenAPIResourceTemplate

def customize_components(
    route: HTTPRoute,
    component: ComponentType,
) -> None:
    """
    Customize OpenAPI components based on route metadata and component type.
    
    This function enhances component descriptions and metadata to provide
    better context to MCP clients.
    
    Args:
        route: The HTTP route from the OpenAPI spec
        component: The MCP component to customize
    """
    logger.debug(f"Customizing component for route: {route.path}")

    # Use x-cortex-mcp-description extension if available
    custom_description = route.extensions.get("x-cortex-mcp-description")
    if custom_description:
        component.description = custom_description
        logger.debug(f"Applied custom description: {custom_description}")

    component.tags.add("cortex-api")
    component.tags.add("openapi")

    for tag in route.tags:
        component.tags.add(tag.lower())

    if isinstance(component, OpenAPITool):
        # Tools are actions, use action-oriented language
        if not custom_description:
            component.description = _format_tool_description(
                route,
                component.description or ""
            )
        # Hide this fully for now.
        component.output_schema = None

        if hasattr(component, 'parameters') and isinstance(component.parameters, dict):
            if "$defs" in component.parameters:
                logger.debug(f"  Found $defs with {len(component.parameters['$defs'])} definitions")
                new_params = {k: v for k, v in component.parameters.items() if k != "$defs"}
                component.parameters = new_params
                logger.debug(f"  After modification: '$defs' in parameters = {'$defs' in component.parameters}")
                mcp_tool = component.to_mcp_tool()
                logger.debug(f"  In to_mcp_tool result: '$defs' in inputSchema = {'$defs' in mcp_tool.inputSchema}")

        # Handle output_schema the same way
        if hasattr(component, 'output_schema') and isinstance(component.output_schema, dict):
            if "$defs" in component.output_schema:
                logger.debug(f"  Found $defs in output_schema with {len(component.output_schema['$defs'])} definitions")
                new_output = {k: v for k, v in component.output_schema.items() if k !=         "$defs"}
                component.output_schema = new_output
                logger.debug(f"  After modification: '$defs' in output_schema = {'$defs' in component.output_schema}")

    elif isinstance(component, OpenAPIResource):
        # Resources are collections, emphasize listing/querying
        if not custom_description:
            component.description = _format_resource_description(
                route,
                component.description or ""
            )

    elif isinstance(component, OpenAPIResourceTemplate):
        # Resource templates are for individual items
        if not custom_description:
            component.description = _format_resource_template_description(
                route,
                component.description or ""
            )

    logger.debug(f"Final description: {component.description}")
    logger.debug(f"Final tags: {component.tags}")


def _format_tool_description(route: HTTPRoute, original: str) -> str:
    """Format description for tool components."""
    method = route.method.upper()
    path = route.path

    if method == "POST":
        action = "Create"
    elif method == "PUT":
        action = "Update"
    elif method == "PATCH":
        action = "Modify"
    elif method == "DELETE":
        action = "Delete"
    else:
        action = "Perform"

    parts = path.strip("/").split("/")
    resource = parts[-1] if parts else "resource"

    resource = resource.replace("{", "").replace("}", "")

    if original:
        return f"{action} {resource}. {original}"
    else:
        return f"{action} {resource} via {method} {path}"


def _format_resource_description(route: HTTPRoute, original: str) -> str:
    """Format description for resource components (collections)."""
    path = route.path

    parts = path.strip("/").split("/")
    resource = parts[-1] if parts else "resources"

    if original:
        return f"List {resource}. {original}"
    else:
        return f"Retrieve a list of {resource}"


def _format_resource_template_description(route: HTTPRoute, original: str) -> str:
    """Format description for resource template components (individual items)."""
    path = route.path

    parts = path.strip("/").split("/")
    resource = "resource"
    for i, part in enumerate(parts):
        if "{" in part and i > 0:
            resource = parts[i-1]
            break

    if resource.endswith("s"):
        resource = resource[:-1]

    if original:
        return f"Get individual {resource}. {original}"
    else:
        return f"Retrieve a specific {resource} by ID"
