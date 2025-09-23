#!/usr/bin/env python3
"""Test if the $ref resolution fix works."""

import json
import asyncio
from src.server import create_mcp_server

async def test_fix():
    # Create the server with our fix
    server = create_mcp_server()

    print(f"Server created: {type(server)}")

    # Check the created tools
    tools = await server.get_tools()

    print(f"Total tools: {len(tools)}")

    # Check a tool that previously had $ref issues
    tool_name = "AzureActiveDirectorySaveConfiguration"
    if tool_name in tools:
        print(f"\nChecking {tool_name}...")

        # Try to access the MCP protocol level to see the actual schema
        # This is a bit hacky but necessary to verify the fix
        for attr in ['_mcp', 'mcp']:
            if hasattr(server, attr):
                mcp = getattr(server, attr)
                if hasattr(mcp, '_server'):
                    internal_server = mcp._server
                    if hasattr(internal_server, 'request_handlers'):
                        handlers = internal_server.request_handlers
                        if 'tools/list' in handlers:
                            result = await handlers['tools/list']()

                            # Find our tool
                            for tool in result.tools:
                                if tool.name == tool_name:
                                    print(f"\nFound tool: {tool.name}")
                                    if tool.inputSchema:
                                        schema = tool.inputSchema.model_dump() if hasattr(tool.inputSchema, 'model_dump') else dict(tool.inputSchema)

                                        # Check if there are any $refs
                                        schema_str = json.dumps(schema)
                                        if '$ref' in schema_str:
                                            print("❌ ISSUE STILL PRESENT: Schema contains $ref")
                                            print(f"Schema: {json.dumps(schema, indent=2)[:500]}...")
                                        else:
                                            print("✅ FIX SUCCESSFUL: No $ref in schema")
                                            print(f"Schema properties: {list(schema.get('properties', {}).keys())}")
                                    return
    else:
        print(f"Tool {tool_name} not found")

asyncio.run(test_fix())