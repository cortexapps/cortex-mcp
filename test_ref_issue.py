#!/usr/bin/env python3
"""Test script to investigate $ref handling in FastMCP.from_openapi"""

import json
from fastmcp import FastMCP
import httpx

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

import asyncio

async def main():
    print("Getting tools from MCP server...")
    tools_dict = await mcp_server.get_tools()
    print(f"Total tools: {len(tools_dict)}")
    return tools_dict

tools_dict = asyncio.run(main())

# Find tools that likely use $ref in their schemas
interesting_tools = [
    "AzureActiveDirectorySaveConfiguration",
    "CatalogGetEntity",
    "CreateApiKey"
]

for tool_name in interesting_tools:
    if tool_name in tools_dict:
        tool = tools_dict[tool_name]
        print(f"\n{'='*60}")
        print(f"Tool: {tool_name}")

        # Check the tool's function signature for input_model
        if hasattr(tool, '__annotations__'):
            print(f"Tool annotations: {tool.__annotations__}")

        # Try to get the input schema from the tool metadata
        if hasattr(tool, '_tool_definition'):
            print(f"Tool definition: {tool._tool_definition}")

        # Try another approach - look at the wrapped function
        import inspect
        sig = inspect.signature(tool)
        print(f"Function signature: {sig}")

        # Get parameters
        for param_name, param in sig.parameters.items():
            print(f"  Parameter {param_name}: {param.annotation}")
            if hasattr(param.annotation, '__annotations__'):
                print(f"    Annotations: {param.annotation.__annotations__}")
            if hasattr(param.annotation, 'model_fields'):
                print(f"    Model fields: {param.annotation.model_fields}")

# Let's also check the raw OpenAPI spec for comparison
print("\n\n" + "="*60)
print("Raw OpenAPI spec for comparison:")
print("="*60)

# Check the AzureActiveDirectorySaveConfiguration endpoint
endpoint = spec["paths"]["/api/v1/active-directory/configuration"]["post"]
print("\nAzureActiveDirectorySaveConfiguration endpoint:")
req_schema = endpoint.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema')
print(f"Request body schema: {req_schema}")

# Look up the referenced schema
if req_schema and '$ref' in req_schema:
    ref_path = req_schema['$ref']
    schema_name = ref_path.split("/")[-1]
    if "components" in spec and "schemas" in spec["components"] and schema_name in spec["components"]["schemas"]:
        print(f"\nActual schema for {schema_name}:")
        actual_schema = spec["components"]["schemas"][schema_name]
        print(json.dumps(actual_schema, indent=2)[:1000] + "...")

# Now check what the tool expects vs what it should be
print("\n\n" + "="*60)
print("ISSUE INVESTIGATION:")
print("="*60)

# Try to access the MCP internals to see what schema was generated
# The issue is likely in how FastMCP resolves the $ref when creating the tool input schema

print("\nChecking if FastMCP properly resolved the $ref...")
print("The $ref points to:", req_schema)
print("The actual schema should have these properties:")
if "components" in spec and "schemas" in spec["components"]:
    schema_name = req_schema['$ref'].split("/")[-1] if req_schema and '$ref' in req_schema else None
    if schema_name and schema_name in spec["components"]["schemas"]:
        actual = spec["components"]["schemas"][schema_name]
        if 'properties' in actual:
            print(f"  Properties: {list(actual['properties'].keys())}")
        if 'required' in actual:
            print(f"  Required: {actual['required']}")

print("\n💡 The issue is likely that FastMCP is not properly resolving the $ref")
print("   and is passing the reference itself as the schema instead of the actual schema.")