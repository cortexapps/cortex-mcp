"""Main entry point for Cortex MCP server."""
import json
from typing import Any

from fastmcp import FastMCP

from .clients.cortex import create_cortex_client
from .components.customizers import customize_components
from .config import Config
from .routes.mappers import custom_route_mapper
from .utils.logging import setup_logging
from .utils.openapi_resolver import resolve_refs

logger = setup_logging()


def load_openapi_spec() -> dict[str, Any]:
    """Load the OpenAPI specification from file."""
    logger.info(f"Loading OpenAPI spec from: {Config.OPENAPI_SPEC_PATH}")

    try:
        with open(Config.OPENAPI_SPEC_PATH) as f:
            spec = json.load(f)

        logger.info("OpenAPI spec loaded successfully")
        return spec

    except FileNotFoundError:
        logger.error(f"OpenAPI spec not found at: {Config.OPENAPI_SPEC_PATH}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in OpenAPI spec: {e}")
        raise


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server."""
    Config.validate()

    openapi_spec = load_openapi_spec()

    # Workaround to resolve all $ref references since FastMCP cannot resolve complex reference chains
    logger.info("Resolving OpenAPI $ref references...")
    openapi_spec = resolve_refs(openapi_spec)
    logger.info("OpenAPI $ref references resolved")

    client = create_cortex_client()

    mcp_server = FastMCP.from_openapi(
        openapi_spec=openapi_spec,
        client=client,
        name=Config.APP_NAME,
        route_map_fn=custom_route_mapper,
        mcp_component_fn=customize_components,
    )

    logger.info(f"MCP server '{Config.APP_NAME}' created successfully")

    return mcp_server


def main() -> None:
    """Main entry point for the application."""
    try:
        mcp_server = create_mcp_server()

        logger.info(f"Starting server with transport: {Config.TRANSPORT}")
        logger.info(f"Host: {Config.HOST}, Port: {Config.PORT}")

        if Config.TRANSPORT == "stdio":
            # Standard I/O transport (for Claude Desktop)
            mcp_server.run()
        elif Config.TRANSPORT == "sse":
            # Server-Sent Events transport (deprecated)
            logger.warning("SSE transport is deprecated, consider using streamable-http")
            mcp_server.run(
                transport="sse",
                host=Config.HOST,
                port=Config.PORT
            )
        else:
            mcp_server.run(
                transport="streamable-http",
                host=Config.HOST,
                port=Config.PORT
            )

    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
