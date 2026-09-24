"""
OpenAPI $ref resolver for FastMCP compatibility.

FastMCP cannot resolve complex reference chains (e.g., $ref -> $defs -> $ref chains).
This script replaces ALL $ref in the entire OpenAPI spec with inline schema definitions.

Since customizers.py currently hides output schemas, $ref resolutions are only visible in INPUT schemas.

Performance note: Currently processes all ~800 endpoints but only ~20 become MCP tools.
The dereferencing work is only visible in PointInTimeMetrics tool, since it's the only
MCP-enabled endpoint with $ref chains in its input schema (output schemas are hidden).

TODO: Optimize to only process MCP-enabled paths
"""

from typing import Any


def resolve_refs(spec: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively resolve all $ref references in an OpenAPI specification.

    This is a workaround for FastMCP's issue with $ref handling where it
    doesn't properly include schema definitions when creating tool input schemas.

    Args:
        spec: OpenAPI specification dictionary

    Returns:
        Modified spec with all $refs resolved inline
    """
    # Create a copy to avoid modifying the original
    spec = spec.copy()

    # Get the components/schemas section for reference resolution
    schemas = spec.get("components", {}).get("schemas", {})

    def resolve_schema(obj: Any, visited: dict[str, int] | None = None) -> Any:
        """Recursively resolve $ref in an object."""
        if visited is None:
            visited = {}

        if isinstance(obj, dict):
            # Check if this is a $ref
            if "$ref" in obj and len(obj) == 1:
                ref_path = obj["$ref"]
                schema_name = ref_path.removeprefix("#/components/schemas/")
                if schema_name == ref_path or schema_name not in schemas:
                    return obj

                # A $ref left in place would dangle once FastMCP moves the schema into a
                # tool's $defs, so a cycle is cut rather than preserved. springdoc emits
                # every polymorphic type as a cycle: the parent lists its subtypes in
                # oneOf, and each subtype extends the parent through allOf. Re-expanding
                # the parent once without its subtypes keeps the fields they inherit.
                depth = visited.get(ref_path, 0)
                if depth >= 2:
                    return _cycle_placeholder(schemas[schema_name])
                target = schemas[schema_name]
                if depth == 1:
                    target = _without_subtypes(target)

                visited[ref_path] = depth + 1
                resolved = resolve_schema(target, visited)
                visited[ref_path] = depth
                return resolved
            else:
                # Recursively process all values in the dict
                result = {}
                for key, value in obj.items():
                    result[key] = resolve_schema(value, visited)
                return result

        elif isinstance(obj, list):
            # Recursively process all items in the list
            return [resolve_schema(item, visited) for item in obj]
        else:
            # Return primitive values as-is
            return obj

    # Resolve refs in all paths
    if "paths" in spec:
        spec["paths"] = resolve_schema(spec["paths"])

    return spec


def _without_subtypes(schema: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in schema.items()
        if key not in ("oneOf", "anyOf", "discriminator")
    }


def _cycle_placeholder(schema: dict[str, Any]) -> dict[str, Any]:
    placeholder: dict[str, Any] = {"type": schema.get("type", "object")}
    if "description" in schema:
        placeholder["description"] = schema["description"]
    return placeholder


# Use if context becomes too large for inline definitions
def resolve_refs_with_defs(spec: dict[str, Any]) -> dict[str, Any]:
    """
    Alternative approach: Keep $refs but ensure $defs section is populated.

    This transforms OpenAPI $refs to JSON Schema format and includes
    all referenced schemas in a $defs section at the root level.

    Args:
        spec: OpenAPI specification dictionary

    Returns:
        Modified spec with $refs pointing to $defs and all definitions included
    """
    # Create a copy to avoid modifying the original
    spec = spec.copy()

    # Get the components/schemas section
    schemas = spec.get("components", {}).get("schemas", {})

    # Create $defs section at root level
    if schemas:
        spec["$defs"] = schemas.copy()

    def transform_refs(obj: Any) -> Any:
        """Transform OpenAPI $refs to JSON Schema $refs."""
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                if key == "$ref" and isinstance(value, str):
                    # Transform the reference format
                    if value.startswith("#/components/schemas/"):
                        schema_name = value.split("/")[-1]
                        result[key] = f"#/$defs/{schema_name}"
                    else:
                        result[key] = value
                else:
                    result[key] = transform_refs(value)
            return result
        elif isinstance(obj, list):
            return [transform_refs(item) for item in obj]
        else:
            return obj

    # Transform all refs in paths
    if "paths" in spec:
        spec["paths"] = transform_refs(spec["paths"])

    return spec
