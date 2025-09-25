"""Tests for OpenAPI $ref resolver."""
import json

from src.utils.openapi_resolver import resolve_refs, resolve_refs_with_defs


class TestOpenAPIResolver:
    """Test suite for OpenAPI $ref resolver."""

    def test_resolve_simple_ref(self):
        """Test resolving a simple $ref to a schema."""
        spec = {
            "paths": {
                "/api/test": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/TestSchema"}
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "TestSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "value": {"type": "integer"}
                        },
                        "required": ["name"]
                    }
                }
            }
        }

        resolved = resolve_refs(spec)

        # Check that the $ref was resolved
        schema = resolved["paths"]["/api/test"]["post"]["requestBody"]["content"]["application/json"]["schema"]
        assert "$ref" not in schema
        assert schema["type"] == "object"
        assert "name" in schema["properties"]
        assert "value" in schema["properties"]
        assert schema["required"] == ["name"]

    def test_resolve_nested_refs(self):
        """Test resolving nested $refs."""
        spec = {
            "paths": {
                "/api/test": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ParentSchema"}
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "ParentSchema": {
                        "type": "object",
                        "properties": {
                            "child": {"$ref": "#/components/schemas/ChildSchema"}
                        }
                    },
                    "ChildSchema": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "string"}
                        }
                    }
                }
            }
        }

        resolved = resolve_refs(spec)

        # Check that all $refs were resolved
        schema = resolved["paths"]["/api/test"]["post"]["requestBody"]["content"]["application/json"]["schema"]
        assert "$ref" not in json.dumps(schema)
        assert schema["properties"]["child"]["properties"]["data"]["type"] == "string"

    def test_resolve_circular_refs(self):
        """Test handling of circular references."""
        spec = {
            "paths": {
                "/api/test": {
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Node"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "Node": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "string"},
                            "parent": {"$ref": "#/components/schemas/Node"}
                        }
                    }
                }
            }
        }

        # Should not raise an exception and should handle circular refs
        resolved = resolve_refs(spec)

        # Should have resolved the top-level ref but left circular ref intact
        schema = resolved["paths"]["/api/test"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
        assert schema["type"] == "object"
        assert "value" in schema["properties"]
        # Circular ref should be preserved to prevent infinite recursion
        assert schema["properties"]["parent"]["$ref"] == "#/components/schemas/Node"

    def test_resolve_refs_in_arrays(self):
        """Test resolving $refs inside arrays."""
        spec = {
            "paths": {
                "/api/test": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Item"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "Item": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        }
                    }
                }
            }
        }

        resolved = resolve_refs(spec)

        schema = resolved["paths"]["/api/test"]["post"]["requestBody"]["content"]["application/json"]["schema"]
        assert schema["type"] == "array"
        assert "$ref" not in schema["items"]
        assert schema["items"]["properties"]["id"]["type"] == "integer"

    def test_preserve_non_schema_refs(self):
        """Test that non-schema $refs are preserved."""
        spec = {
            "paths": {
                "/api/test": {
                    "get": {
                        "parameters": [
                            {"$ref": "#/components/parameters/CommonParam"}
                        ]
                    }
                }
            },
            "components": {
                "parameters": {
                    "CommonParam": {
                        "name": "test",
                        "in": "query",
                        "schema": {"type": "string"}
                    }
                }
            }
        }

        resolved = resolve_refs(spec)

        # Non-schema refs should be preserved
        param_ref = resolved["paths"]["/api/test"]["get"]["parameters"][0]
        assert param_ref == {"$ref": "#/components/parameters/CommonParam"}

    def test_resolve_refs_with_defs(self):
        """Test the alternative approach using $defs."""
        spec = {
            "paths": {
                "/api/test": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/TestSchema"}
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "TestSchema": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}}
                    }
                }
            }
        }

        resolved = resolve_refs_with_defs(spec)

        # Should have $defs section
        assert "$defs" in resolved
        assert "TestSchema" in resolved["$defs"]

        # Refs should be transformed to JSON Schema format
        schema_ref = resolved["paths"]["/api/test"]["post"]["requestBody"]["content"]["application/json"]["schema"]
        assert schema_ref["$ref"] == "#/$defs/TestSchema"

    def test_no_components_section(self):
        """Test handling when components section is missing."""
        spec = {
            "paths": {
                "/api/test": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "OK"
                            }
                        }
                    }
                }
            }
        }

        # Should not raise an exception
        resolved = resolve_refs(spec)
        assert resolved == spec

    def test_original_spec_unchanged(self):
        """Test that the original spec is not modified."""
        spec = {
            "paths": {
                "/api/test": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/TestSchema"}
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "TestSchema": {"type": "object"}
                }
            }
        }

        original_json = json.dumps(spec, sort_keys=True)
        resolve_refs(spec)

        # Original should be unchanged
        assert json.dumps(spec, sort_keys=True) == original_json
