#!/bin/bash

# Test script for Docker MCP server

echo "Testing Docker MCP server..."

# Build the image first
echo "1. Building Docker image..."
docker build -t cortex-mcp .

# Test 1: Basic initialization test
echo -e "\n2. Testing server initialization..."
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "0.1.0", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}, "id": 1}' | \
docker run --rm -i --env CORTEX_API_TOKEN="${CORTEX_API_TOKEN}" cortex-mcp | \
head -n 1

# Test 2: List available tools
echo -e "\n3. Testing list tools..."
echo '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}' | \
docker run --rm -i --env CORTEX_API_TOKEN="${CORTEX_API_TOKEN}" cortex-mcp | \
head -n 1

# Test 3: Test with invalid request
echo -e "\n4. Testing error handling..."
echo '{"jsonrpc": "2.0", "method": "invalid/method", "params": {}, "id": 3}' | \
docker run --rm -i --env CORTEX_API_TOKEN="${CORTEX_API_TOKEN}" cortex-mcp 2>&1 | \
head -n 1

echo -e "\nTests complete!"