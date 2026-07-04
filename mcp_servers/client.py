"""Bounded in-memory MCP client adapter for approved local servers."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from schemas.mcp import MCPInvocation, MCPInvocationResult

from mcp_servers import case_data_server, pathway_rules_server, policy_evidence_server
from mcp_servers.common import MAX_MCP_INPUT_CHARS, MAX_MCP_OUTPUT_CHARS, MCPCapabilityError
from mcp_servers.registry import get_server_definition

MAX_CLIENT_CALLS = 40


class BoundedMCPClient:
    """Allow-listed local MCP adapter with audit records."""

    def __init__(self) -> None:
        self.invocations: list[MCPInvocationResult] = []

    def call_tool(self, server_name: str, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Call one approved local MCP tool."""
        definition = get_server_definition(server_name)
        if tool_name not in definition.approved_tools:
            raise MCPCapabilityError(f"unapproved MCP tool: {server_name}.{tool_name}")
        tool = _tool_callable(server_name, tool_name)
        return self._invoke(
            server_name,
            tool_name,
            "tool",
            arguments,
            lambda: tool(**arguments),
        )

    def read_resource(self, server_name: str, resource_uri: str) -> Any:
        """Read one approved local MCP resource."""
        definition = get_server_definition(server_name)
        if not _resource_allowed(resource_uri, definition.approved_resources):
            raise MCPCapabilityError(f"unapproved MCP resource: {resource_uri}")
        return self._invoke(
            server_name,
            resource_uri,
            "resource",
            {"uri": resource_uri},
            lambda: _resource_callable(server_name)(resource_uri),
        )

    def _invoke(
        self,
        server_name: str,
        capability_name: str,
        capability_type: str,
        arguments: dict[str, Any],
        func: Callable[[], Any],
    ) -> Any:
        if len(self.invocations) >= MAX_CLIENT_CALLS:
            raise MCPCapabilityError("maximum MCP call limit exceeded")
        if len(str(arguments)) > MAX_MCP_INPUT_CHARS:
            raise MCPCapabilityError("MCP input exceeds configured size limit")
        started = datetime.now(UTC)
        start_counter = perf_counter()
        invocation = MCPInvocation(
            server_name=server_name,
            capability_name=capability_name,
            capability_type=capability_type,
            input_summary=_redact(arguments),
            started_at=started,
        )
        try:
            output = func()
            if len(str(output)) > MAX_MCP_OUTPUT_CHARS:
                raise MCPCapabilityError("MCP output exceeds configured size limit")
            success = True
            error = None
            return output
        except Exception as exc:
            success = False
            error = str(exc)
            raise
        finally:
            self.invocations.append(
                MCPInvocationResult(
                    invocation=invocation,
                    output_summary=_summarise(output) if "output" in locals() else {},
                    completed_at=datetime.now(UTC),
                    duration_ms=round((perf_counter() - start_counter) * 1000, 2),
                    success=success if "success" in locals() else False,
                    error=error if "error" in locals() else None,
                )
            )


def _tool_callable(server_name: str, tool_name: str) -> Callable[..., Any]:
    tool_maps: dict[str, dict[str, Callable[..., Any]]] = {
        "case-data": {
            "get_case": case_data_server.get_case,
            "list_cases": case_data_server.list_cases,
            "list_cases_by_pathway": case_data_server.list_cases_by_pathway_tool,
            "validate_case": case_data_server.validate_case,
        },
        "pathway-rules": {
            "get_pathway_rule": pathway_rules_server.get_pathway_rule,
            "list_pathway_rules": pathway_rules_server.list_pathway_rules,
            "calculate_elapsed_time": pathway_rules_server.calculate_elapsed_time,
            "determine_breach_status": pathway_rules_server.determine_breach_status,
            "run_pathway_assessment": pathway_rules_server.run_pathway_assessment,
        },
        "policy-evidence": {
            "search_evidence": policy_evidence_server.search_evidence,
            "get_evidence": policy_evidence_server.get_evidence,
            "list_evidence": policy_evidence_server.list_evidence,
            "get_evidence_for_pathway": policy_evidence_server.get_evidence_for_pathway,
        },
    }
    return tool_maps[server_name][tool_name]


def _resource_callable(server_name: str) -> Callable[[str], Any]:
    resources: dict[str, Callable[[str], Any]] = {
        "case-data": case_data_server.read_case_resource,
        "pathway-rules": pathway_rules_server.read_pathway_resource,
        "policy-evidence": policy_evidence_server.read_evidence_resource,
    }
    return resources[server_name]


def _resource_allowed(resource_uri: str, approved: list[str]) -> bool:
    for pattern in approved:
        if "{" not in pattern and resource_uri == pattern:
            return True
        prefix = pattern.split("{", 1)[0]
        if "{" in pattern and resource_uri.startswith(prefix) and ".." not in resource_uri:
            return True
    return False


def _redact(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        key: (
            "<redacted>"
            if any(token in key.lower() for token in ["key", "token", "secret"])
            else value
        )
        for key, value in arguments.items()
    }


def _summarise(output: Any) -> dict[str, Any]:
    if isinstance(output, dict):
        return {"keys": sorted(output.keys())[:8]}
    if isinstance(output, list):
        return {"items": len(output)}
    return {"type": type(output).__name__}
