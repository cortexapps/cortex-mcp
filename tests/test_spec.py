"""Tests for the bundled OpenAPI spec."""
import json
from pathlib import Path

from src.components.customizers import ACCESS_VALUES

SPEC_PATH = Path(__file__).parent.parent / "swagger.json"


class TestBundledSpec:
    """Test suite for the swagger.json the server ships with."""

    def test_mcp_tools_declare_valid_access(self):
        """Test that MCP-enabled operations set a valid x-cortex-mcp-access.

        Every operation other than a GET must set it. Without it, or with an
        unknown value, the tool is published as destructive even if it only reads.
        """
        spec = json.loads(SPEC_PATH.read_text())

        invalid = [
            f"{method.upper()} {path}"
            for path, item in spec["paths"].items()
            for method, operation in item.items()
            if isinstance(operation, dict)
            and operation.get("x-cortex-mcp-enabled") == "true"
            and (method != "get" or "x-cortex-mcp-access" in operation)
            and operation.get("x-cortex-mcp-access") not in ACCESS_VALUES
        ]

        assert not invalid, (
            f"Set x-cortex-mcp-access to one of {', '.join(ACCESS_VALUES)} on: "
            f"{', '.join(invalid)}"
        )
