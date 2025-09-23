#!/usr/bin/env python3
"""Test the actual MCP protocol to see tool schemas"""

import json
import sys
import asyncio

# Simulate MCP client-server interaction
async def test_mcp_protocol():
    # Import the server module
    from src.server import create_mcp_server

    # Create the server
    server = create_mcp_server()

    # Access the internal MCP server to call tools/list
    # FastMCP wraps an MCP server
    print(f"Server type: {type(server)}")

    # Try different approaches to get at the MCP server
    for attr in ['_mcp', 'mcp', '_server', 'server']:
        if hasattr(server, attr):
            print(f"Found attribute: {attr}")
            inner = getattr(server, attr)
            print(f"  Type: {type(inner)}")

            # Check if this has request_handlers
            if hasattr(inner, 'request_handlers'):
                print(f"  Has request_handlers!")
                handlers = inner.request_handlers

                if 'tools/list' in handlers:
                    print("\n  Calling tools/list handler...")
                    result = await handlers['tools/list']()
                    print(f"  Got {len(result.tools)} tools")

                    # Find our problematic tool
                    for tool in result.tools:
                        if 'Azure' in tool.name and 'Save' in tool.name:
                            print(f"\n  Found tool: {tool.name}")
                            if tool.inputSchema:
                                schema = tool.inputSchema.model_dump() if hasattr(tool.inputSchema, 'model_dump') else dict(tool.inputSchema)
                                print(f"  Input Schema:")
                                print(json.dumps(schema, indent=4))

                                # Check for $ref
                                if '$ref' in json.dumps(schema):
                                    print("\n  ⚠️ PROBLEM: Unresolved $ref in schema!")
                                else:
                                    print("\n  ✅ Schema looks resolved")
                            break
                    break

            # Also check for _server nested deeper
            if hasattr(inner, '_server'):
                print(f"  Has _server attribute")
                deeper = inner._server
                if hasattr(deeper, 'request_handlers'):
                    print(f"    Has request_handlers!")
                    handlers = deeper.request_handlers

                    if 'tools/list' in handlers:
                        print("\n    Calling tools/list handler...")
                        result = await handlers['tools/list']()
                        print(f"    Got {len(result.tools)} tools")

                        # Find our problematic tool
                        for tool in result.tools:
                            if 'Azure' in tool.name and 'Save' in tool.name:
                                print(f"\n    Found tool: {tool.name}")
                                if tool.inputSchema:
                                    schema = tool.inputSchema.model_dump() if hasattr(tool.inputSchema, 'model_dump') else dict(tool.inputSchema)
                                    print(f"    Input Schema:")
                                    print(json.dumps(schema, indent=4))

                                    # Check for $ref
                                    if '$ref' in json.dumps(schema):
                                        print("\n    ⚠️ PROBLEM: Unresolved $ref in schema!")
                                    else:
                                        print("\n    ✅ Schema looks resolved")
                                break
                        break

# Run the test
asyncio.run(test_mcp_protocol())