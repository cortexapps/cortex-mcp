"""Tests for path-traversal input-validation safeguards."""
from types import SimpleNamespace

import pytest
from fastmcp.exceptions import ToolError

from src.security import (
    PathTraversalGuardMiddleware,
    contains_path_traversal,
    extract_path_param_names,
)


class TestContainsPathTraversal:
    """Values that must be rejected mirror the payloads in the customer report."""

    @pytest.mark.parametrize(
        "value",
        [
            "../../v1/catalog/entities/services?",
            "../../internal/health?",
            "../../internal/v1/catalog?",
            "../../nonexistent/path",
            "..%5C..%5Cinternal/health",
            "..%2f..%2finternal",
            "%2e%2e/internal",
            "a/b",
            "a\\b",
            "tag;matrix=1",
            "with\x00null",
        ],
    )
    def test_rejects_traversal_payloads(self, value):
        assert contains_path_traversal(value) is True

    @pytest.mark.parametrize(
        "value",
        [
            "test",
            "my-service",
            "123",
            "service-tag_v2",
            "Some Display Name",
            "a.b.c",  # dots alone are fine; only ".." is a dot-segment
        ],
    )
    def test_allows_legitimate_identifiers(self, value):
        assert contains_path_traversal(value) is False


class TestExtractPathParamNames:
    def test_extracts_template_placeholders_and_declared_path_params(self):
        spec = {
            "paths": {
                "/api/v1/catalog/entities/{tagOrId}/custom-data": {
                    "get": {
                        "parameters": [
                            {"name": "context", "in": "query"},
                            {"name": "key", "in": "path"},
                        ]
                    }
                },
                "/api/v1/dependencies/{callerTag}": {"get": {}},
            }
        }
        assert extract_path_param_names(spec) == {"tagOrId", "key", "callerTag"}

    def test_query_only_params_are_excluded(self):
        spec = {
            "paths": {
                "/api/v1/search": {
                    "get": {"parameters": [{"name": "context", "in": "query"}]}
                }
            }
        }
        assert extract_path_param_names(spec) == set()


def _context(name: str, arguments: dict):
    return SimpleNamespace(message=SimpleNamespace(name=name, arguments=arguments))


class TestPathTraversalGuardMiddleware:
    @pytest.fixture
    def middleware(self):
        return PathTraversalGuardMiddleware({"tagOrId", "callerTag", "key"})

    async def _call_next(self, context):
        return "forwarded"

    @pytest.mark.asyncio
    async def test_blocks_traversal_in_path_param(self, middleware):
        context = _context(
            "getCustomDataForEntity",
            {"tagOrId": "../../internal/health?", "context": ""},
        )
        with pytest.raises(ToolError):
            await middleware.on_call_tool(context, self._call_next)

    @pytest.mark.asyncio
    async def test_allows_traversal_like_value_in_non_path_param(self, middleware):
        # `context` is not a path parameter, so slashes in it are legitimate.
        context = _context(
            "getCustomDataForEntity",
            {"tagOrId": "my-service", "context": "look in ../docs for details"},
        )
        assert await middleware.on_call_tool(context, self._call_next) == "forwarded"

    @pytest.mark.asyncio
    async def test_allows_legitimate_call(self, middleware):
        context = _context("getEntityDetails", {"tagOrId": "my-service"})
        assert await middleware.on_call_tool(context, self._call_next) == "forwarded"

    @pytest.mark.asyncio
    async def test_allows_call_with_no_arguments(self, middleware):
        context = _context("listAllEntities", {})
        assert await middleware.on_call_tool(context, self._call_next) == "forwarded"
