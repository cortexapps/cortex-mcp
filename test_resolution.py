#!/usr/bin/env python3
"""Test the ref resolution directly."""

import json
from src.utils.openapi_resolver import resolve_refs

# Load the original spec
with open("swagger.json") as f:
    original_spec = json.load(f)

# Resolve refs
resolved_spec = resolve_refs(original_spec)

# Check a specific endpoint that uses $ref
endpoint = original_spec["paths"]["/api/v1/active-directory/configuration"]["post"]
resolved_endpoint = resolved_spec["paths"]["/api/v1/active-directory/configuration"]["post"]

print("ORIGINAL:")
print(json.dumps(endpoint.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema'), indent=2))

print("\nRESOLVED:")
print(json.dumps(resolved_endpoint.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema'), indent=2)[:500] + "...")