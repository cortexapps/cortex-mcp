"""Tests for the bundled OpenAPI spec."""
import json
from pathlib import Path

SPEC_PATH = Path(__file__).parent.parent / "swagger.json"


class TestBundledSpec:
    """Test suite for the swagger.json the server ships with."""

    def test_mcp_writes_declare_access(self):
        """Test that every MCP-enabled non-GET operation sets x-cortex-mcp-access.

        Without it the tool is published as destructive, even if it only reads.
        """
        spec = json.loads(SPEC_PATH.read_text())

        undeclared = [
            f"{method.upper()} {path}"
            for path, item in spec["paths"].items()
            for method, operation in item.items()
            if isinstance(operation, dict)
            and method != "get"
            and operation.get("x-cortex-mcp-enabled") == "true"
            and "x-cortex-mcp-access" not in operation
        ]

        assert undeclared == []
