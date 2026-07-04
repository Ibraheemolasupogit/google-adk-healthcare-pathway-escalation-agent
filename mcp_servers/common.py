"""Shared helpers for local MCP-compatible servers."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

MAX_MCP_INPUT_CHARS = 4000
MAX_MCP_OUTPUT_CHARS = 20000


class MCPCapabilityError(ValueError):
    """Raised when a local MCP capability fails safely."""


def create_server(name: str, instructions: str) -> FastMCP:
    """Create a local FastMCP server configured for safe development use."""
    return FastMCP(name=name, instructions=instructions, host="127.0.0.1", port=0)


def validate_no_path_traversal(value: str) -> None:
    """Reject path traversal markers in identifier-like values."""
    if ".." in value or "/" in value or "\\" in value:
        raise MCPCapabilityError("path traversal and arbitrary path access are not allowed")


def validate_input_size(payload: Any) -> None:
    """Reject oversized MCP inputs."""
    if len(str(payload)) > MAX_MCP_INPUT_CHARS:
        raise MCPCapabilityError("MCP input exceeds configured size limit")


def validate_output_size(payload: Any) -> None:
    """Reject oversized MCP outputs."""
    if len(str(payload)) > MAX_MCP_OUTPUT_CHARS:
        raise MCPCapabilityError("MCP output exceeds configured size limit")


def with_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    """Attach common demonstration metadata to MCP responses."""
    return {
        **payload,
        "demonstration_only": True,
        "validation_required": True,
        "warning": "Demonstration-only data. Validate before operational use.",
    }
