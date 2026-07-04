"""Static allow-listed MCP server registry."""

from __future__ import annotations

from schemas.agent import ExecutionMode
from schemas.mcp import MCPResourceDescriptor, MCPServerDefinition, MCPToolDescriptor, MCPTransport

SERVER_REGISTRY: dict[str, MCPServerDefinition] = {
    "case-data": MCPServerDefinition(
        name="case-data",
        transport=MCPTransport.STDIO,
        entry_point="python3 -m mcp_servers.case_data_server",
        approved_tools=["get_case", "list_cases", "list_cases_by_pathway", "validate_case"],
        approved_resources=["case://synthetic/index", "case://synthetic/{case_id}"],
        timeout_seconds=5,
        maximum_calls=20,
        enabled_modes=[ExecutionMode.MOCK_MCP],
    ),
    "pathway-rules": MCPServerDefinition(
        name="pathway-rules",
        transport=MCPTransport.STDIO,
        entry_point="python3 -m mcp_servers.pathway_rules_server",
        approved_tools=[
            "get_pathway_rule",
            "list_pathway_rules",
            "calculate_elapsed_time",
            "determine_breach_status",
            "run_pathway_assessment",
        ],
        approved_resources=["pathway://rules/index", "pathway://rules/{pathway_code}"],
        timeout_seconds=5,
        maximum_calls=20,
        enabled_modes=[ExecutionMode.MOCK_MCP],
    ),
    "policy-evidence": MCPServerDefinition(
        name="policy-evidence",
        transport=MCPTransport.STDIO,
        entry_point="python3 -m mcp_servers.policy_evidence_server",
        approved_tools=[
            "search_evidence",
            "get_evidence",
            "list_evidence",
            "get_evidence_for_pathway",
        ],
        approved_resources=[
            "evidence://local/index",
            "evidence://local/{evidence_id}",
            "evidence://local/pathway/{pathway_code}",
        ],
        timeout_seconds=5,
        maximum_calls=20,
        enabled_modes=[ExecutionMode.MOCK_MCP],
    ),
}


def get_server_definition(server_name: str) -> MCPServerDefinition:
    """Return one approved MCP server definition."""
    try:
        return SERVER_REGISTRY[server_name]
    except KeyError as exc:
        raise ValueError(f"unknown MCP server: {server_name}") from exc


def list_server_definitions() -> list[MCPServerDefinition]:
    """Return all approved MCP server definitions."""
    return list(SERVER_REGISTRY.values())


def list_tool_descriptors() -> list[MCPToolDescriptor]:
    """Return approved MCP tool descriptors."""
    return [
        MCPToolDescriptor(server_name=server.name, tool_name=tool, description=f"Approved {tool}")
        for server in SERVER_REGISTRY.values()
        for tool in server.approved_tools
    ]


def list_resource_descriptors() -> list[MCPResourceDescriptor]:
    """Return approved MCP resource descriptors."""
    return [
        MCPResourceDescriptor(
            server_name=server.name,
            resource_uri=resource,
            description=f"Approved resource {resource}",
        )
        for server in SERVER_REGISTRY.values()
        for resource in server.approved_resources
    ]


TOOL_ACCESS_MATRIX: dict[str, list[str]] = {
    "Coordinator Agent": [
        "case-data.get_case",
        "case-data.validate_case",
        "pathway-rules.run_pathway_assessment",
    ],
    "Pathway Agent": [
        "pathway-rules.get_pathway_rule",
        "pathway-rules.calculate_elapsed_time",
        "pathway-rules.determine_breach_status",
    ],
    "Risk Agent": ["pathway-rules.run_pathway_assessment"],
    "Evidence Agent": [
        "policy-evidence.search_evidence",
        "policy-evidence.get_evidence",
        "policy-evidence.get_evidence_for_pathway",
    ],
    "Escalation Agent": [],
    "Review Agent": [],
}
