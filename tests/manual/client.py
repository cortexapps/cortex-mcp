#!/usr/bin/env python3
"""
Simple FastMCP Client Test
Uses FastMCP's built-in Client to test your server
"""

import asyncio
import sys

from fastmcp import Client


async def test_server(server_url):
    """Test your FastMCP server"""
    print(f"Testing server: {server_url}")

    async with Client(server_url) as client:
        print("✅ Connected!")



        tools = await client.list_tools()

        resources = await client.list_resources()
        resource_templates = await client.list_resource_templates()
        print(f"\n📦 Found {len(tools)} tools:")

        print(f"\n📦 Found {len(resources)} resources:")

        print(f"\n📦 Found {len(resource_templates)} resource templates:")

        for resource in resources:
            print(f"  📄 {resource.name}: {resource}")

        for tool in tools:
            print(f"  🔧 {tool.name}: {tool}")

        # Test the first tool with empty args
        # if tools:
        #     tool = tools[0]
        #     print(f"\n🧪 Testing '{tool.name}'...")
        #
        #     # Provide sample arguments based on tool name
        #     args = {}
        #     if tool.name == "process_data":
        #         args = {"uri": "https://example.com/sample.txt"}
        #
        #     try:
        #         result = await client.call_tool(tool.name, args)
        #         print("✅ Success!")
        #         for content in result:
        #             print(f"   📄 {content}")
        #     except Exception as e:
        #         print(f"⚠️  Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python client.py <host:port>")
        print("Example: python client.py localhost:8000")
        print("Example: python client.py http://localhost:8000")
        sys.exit(1)

    server_url = sys.argv[1]

    # Add http:// if not present
    if not server_url.startswith(('http://', 'https://', 'ws://', 'wss://')):
        server_url = f"http://{server_url}"

    asyncio.run(test_server(server_url))
