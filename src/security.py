"""Input-validation safeguards for OpenAPI-derived MCP tools.

FastMCP interpolates tool arguments into backend URL path templates (e.g.
``/api/v1/catalog/entities/{tagOrId}/custom-data``). A path-parameter value that
contains a separator or dot-segment can break out of its URL segment and route
the request outside the intended ``/api/v1`` prefix — a path traversal that lets
a caller probe undocumented backend routes. These guards reject such values for
the parameters that are interpolated into the request path.
"""
from __future__ import annotations

import re
from typing import Any

from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext

from .utils.logging import get_logger

logger = get_logger(__name__)

# Sequences that let a path parameter escape its URL segment: raw separators and
# dot-segments plus their percent- and backslash-encodings. Matched
# case-insensitively against the raw (pre-substitution) argument value, so
# encoded variants are caught before the backend can decode them.
_TRAVERSAL_TOKENS: tuple[str, ...] = (
    "/",
    "\\",
    "..",
    ";",
    "%2f",  # /
    "%5c",  # \
    "%2e",  # .
)


def contains_path_traversal(value: str) -> bool:
    """Return True if ``value`` is unsafe to interpolate into a URL path segment."""
    lowered = value.lower()
    if any(token in lowered for token in _TRAVERSAL_TOKENS):
        return True
    # Control characters (including NUL) can truncate or confuse routing.
    return any(ord(char) < 0x20 for char in value)


def extract_path_param_names(openapi_spec: dict[str, Any]) -> set[str]:
    """Collect every parameter name that appears as a URL path parameter.

    Only path parameters are interpolated into the request path, so they are the
    values that must stay free of separators. Query and body parameters (e.g. a
    free-text ``context``) are intentionally excluded.
    """
    names: set[str] = set()
    for path, path_item in openapi_spec.get("paths", {}).items():
        # Placeholders in the path template are authoritative path parameters.
        names.update(re.findall(r"\{([^}]+)\}", path))
        if not isinstance(path_item, dict):
            continue
        # Explicit `in: path` declarations at the path or operation level.
        parameter_lists = [path_item.get("parameters")]
        parameter_lists += [
            operation.get("parameters")
            for operation in path_item.values()
            if isinstance(operation, dict)
        ]
        for parameters in parameter_lists:
            for parameter in parameters or []:
                if (
                    isinstance(parameter, dict)
                    and parameter.get("in") == "path"
                    and parameter.get("name")
                ):
                    names.add(parameter["name"])
    return names


class PathTraversalGuardMiddleware(Middleware):
    """Reject tool calls whose path-parameter arguments contain traversal sequences.

    Runs before the request is forwarded to the backend, so a malicious value is
    never composed into a backend URL.
    """

    def __init__(self, path_param_names: set[str]):
        self._path_param_names = set(path_param_names)

    async def on_call_tool(
        self,
        context: MiddlewareContext,
        call_next: CallNext,
    ) -> Any:
        arguments = context.message.arguments or {}
        for name, value in arguments.items():
            if (
                name in self._path_param_names
                and isinstance(value, str)
                and contains_path_traversal(value)
            ):
                logger.warning(
                    "Blocked tool call %r: path parameter %r contained an illegal sequence",
                    context.message.name,
                    name,
                )
                raise ToolError(
                    f"Invalid value for '{name}': path identifiers may not contain "
                    "'/', '\\', '..', ';', or their encoded forms."
                )
        return await call_next(context)
