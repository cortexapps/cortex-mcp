#!/usr/bin/env python3
"""Test to see what schemas FastMCP generates for tools with $ref"""

import json
import asyncio
from fastmcp import FastMCP
import httpx
import logging

# Suppress info logs
logging.getLogger("fastmcp").setLevel(logging.WARNING)

# Load the OpenAPI spec
with open("swagger.json") as f:
    spec = json.load(f)

# Create a dummy client
client = httpx.Client(base_url="https://api.getcortexapp.com")

# Create MCP server from OpenAPI spec
mcp_server = FastMCP.from_openapi(
    openapi_spec=spec,
    client=client,
    name="test-cortex"
)

print(f"MCP server type: {type(mcp_server)}")
print(f"MCP server dir (non-private): {[x for x in dir(mcp_server) if not x.startswith('_')][:10]}")

# Check for _mcp attribute (common internal attribute)
if hasattr(mcp_server, '_mcp'):
    print("Found _mcp attribute")
    inner = mcp_server._mcp
    print(f"Inner type: {type(inner)}")
    print(f"Inner dir: {[x for x in dir(inner) if not x.startswith('_')][:10]}")

    if hasattr(inner, '_server'):
        print("Found _server in _mcp")
        server = inner._server
        if hasattr(server, 'request_handlers'):
            handlers = server.request_handlers
            print(f"Available handlers: {list(handlers.keys())}")

            if 'tools/list' in handlers:
                async def get_tools():
                    result = await handlers['tools/list']()
                    return result

                result = asyncio.run(get_tools())
                print(f"\nTotal tools found: {len(result.tools)}")

                # Check a specific tool
                for tool in result.tools[:3]:  # Just check first 3
                    print(f"\nTool: {tool.name}")
                    if tool.inputSchema:
                        schema = tool.inputSchema.model_dump() if hasattr(tool.inputSchema, 'model_dump') else dict(tool.inputSchema)
                        print(f"Schema type: {type(tool.inputSchema)}")
                        print(f"Schema: {json.dumps(schema, indent=2)[:200]}...")

                # Look specifically for our problem tool
                azure_tool = [t for t in result.tools if t.name == "AzureActiveDirectorySaveConfiguration"]
                if azure_tool:
                    tool = azure_tool[0]
                    print(f"\n{'='*60}")
                    print(f"FOUND PROBLEM TOOL: {tool.name}")
                    print(f"{'='*60}")
                    if tool.inputSchema:
                        schema = tool.inputSchema.model_dump() if hasattr(tool.inputSchema, 'model_dump') else dict(tool.inputSchema)
                        print(f"Full Input Schema:")
                        print(json.dumps(schema, indent=2))

                        # Check if it has $ref
                        schema_str = json.dumps(schema)
                        if '$ref' in schema_str:
                            print("\n⚠️  ISSUE CONFIRMED: Schema contains unresolved $ref!")
                            print("The $ref should have been resolved to the actual schema.")
                        else:
                            print("\n✅ No $ref found in schema - it may be resolved correctly")

# Also check what the schema SHOULD be
print(f"\n{'='*60}")
print("WHAT THE SCHEMA SHOULD BE:")
print(f"{'='*60}")

endpoint = spec["paths"]["/api/v1/active-directory/configuration"]["post"]
req_body = endpoint.get('requestBody', {})
if req_body:
    schema_ref = req_body.get('content', {}).get('application/json', {}).get('schema', {})
    print(f"OpenAPI spec has: {schema_ref}")

    if '$ref' in schema_ref:
        ref_path = schema_ref['$ref']
        schema_name = ref_path.split('/')[-1]
        if 'components' in spec and 'schemas' in spec['components'] and schema_name in spec['components']['schemas']:
            actual_schema = spec['components']['schemas'][schema_name]
            print(f"\nThe {schema_name} schema should be:")
            print(json.dumps(actual_schema, indent=2)[:600] + "...")