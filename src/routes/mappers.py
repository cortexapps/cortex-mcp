"""Route mapping logic for MCP server."""

from fastmcp.server.openapi import HTTPRoute, MCPType

from ..utils.logging import get_logger

logger = get_logger(__name__)


def custom_route_mapper(route: HTTPRoute, mcp_type: MCPType) -> MCPType | None:
    """
    Map OpenAPI routes to MCP types based on custom logic.
    
    Simple logic: Include routes with x-cortex-mcp-enabled="true" as tools,
    exclude everything else.
    
    Args:
        route: The HTTP route from the OpenAPI spec
        mcp_type: The default MCP type suggested by FastMCP
        
    Returns:
        MCPType or None to use default mapping
    """
    logger.debug(f"Evaluating route: {route.method} {route.path}")
    logger.debug(f"Tags: {route.tags}")

    if route.extensions.get("x-cortex-mcp-enabled") == "false":
        return MCPType.EXCLUDE
    elif route.extensions.get("x-cortex-mcp-enabled") == "true":
        return MCPType.TOOL
    
    return MCPType.EXCLUDE  # TODO UNDO THIS.
