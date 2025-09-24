"""OpenAPI $ref resolver for FastMCP compatibility."""

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

    def resolve_schema(obj: Any, visited: set[str] | None = None) -> Any:
        """Recursively resolve $ref in an object."""
        if visited is None:
            visited = set()

        if isinstance(obj, dict):
            # Check if this is a $ref
            if "$ref" in obj and len(obj) == 1:
                ref_path = obj["$ref"]

                # Prevent infinite recursion
                if ref_path in visited:
                    # Return the ref as-is to avoid infinite loop
                    return obj

                visited.add(ref_path)

                # Extract schema name from reference
                if ref_path.startswith("#/components/schemas/"):
                    schema_name = ref_path.split("/")[-1]
                    if schema_name in schemas:
                        # Recursively resolve the referenced schema
                        resolved = resolve_schema(schemas[schema_name].copy(), visited)
                        visited.remove(ref_path)
                        return resolved

                # If we can't resolve, return as-is
                visited.remove(ref_path)
                return obj
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