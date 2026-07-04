"""Unit tests for local MCP interoperability."""

from __future__ import annotations

from importlib.metadata import version

import pytest
from mcp.server.fastmcp import FastMCP
from mcp_servers.case_data_server import create_case_data_server
from mcp_servers.client import MAX_CLIENT_CALLS, BoundedMCPClient
from mcp_servers.common import MCPCapabilityError
from mcp_servers.pathway_rules_server import create_pathway_rules_server
from mcp_servers.policy_evidence_server import create_policy_evidence_server
from mcp_servers.registry import (
    TOOL_ACCESS_MATRIX,
    get_server_definition,
    list_resource_descriptors,
    list_server_definitions,
    list_tool_descriptors,
)
from schemas.agent import ExecutionMode
from schemas.assessment import PathwayAssessment
from services.agent_orchestrator import run_agent_assessment
from services.assessment_service import assess_case
from tools.case_tools import get_case_by_id
from tools.exceptions import DomainValidationError

CASE_ID = "SYN-CANCER-2WW-001"


def test_mcp_package_version_and_fastmcp_servers() -> None:
    assert version("mcp") == "1.28.1"
    assert isinstance(create_case_data_server(), FastMCP)
    assert isinstance(create_pathway_rules_server(), FastMCP)
    assert isinstance(create_policy_evidence_server(), FastMCP)


def test_registry_is_static_and_allow_listed() -> None:
    servers = list_server_definitions()

    assert {server.name for server in servers} == {
        "case-data",
        "pathway-rules",
        "policy-evidence",
    }
    server_names = {server.name for server in servers}
    assert all(server.transport.value == "stdio" for server in servers)
    assert all(ExecutionMode.MOCK_MCP in server.enabled_modes for server in servers)
    assert all(tool.server_name in server_names for tool in list_tool_descriptors())
    assert all(
        resource.server_name in {server.name for server in servers}
        for resource in list_resource_descriptors()
    )
    with pytest.raises(ValueError, match="unknown MCP server"):
        get_server_definition("external")


def test_mcp_client_rejects_unapproved_tool_and_resource() -> None:
    client = BoundedMCPClient()

    with pytest.raises(MCPCapabilityError, match="unapproved MCP tool"):
        client.call_tool("case-data", "read_file", {"path": "/etc/passwd"})
    with pytest.raises(MCPCapabilityError, match="unapproved MCP resource"):
        client.read_resource("case-data", "file:///etc/passwd")


def test_case_data_tools_validate_identity_and_path_controls() -> None:
    client = BoundedMCPClient()
    case = client.call_tool("case-data", "get_case", {"case_id": CASE_ID})

    assert case["case"]["case_id"] == CASE_ID
    with pytest.raises(ValueError, match="prohibited identity fields"):
        client.call_tool(
            "case-data",
            "validate_case",
            {"case_payload": {**case["case"], "nhs_number": "9999999999"}},
        )
    with pytest.raises(MCPCapabilityError):
        client.call_tool("case-data", "get_case", {"case_id": "../secret"})


def test_pathway_assessment_matches_direct_deterministic_engine() -> None:
    client = BoundedMCPClient()
    via_mcp = client.call_tool(
        "pathway-rules",
        "run_pathway_assessment",
        {"case_id": CASE_ID},
    )["assessment"]
    direct = assess_case(get_case_by_id(CASE_ID))

    assert (
        PathwayAssessment.model_validate(via_mcp).model_copy(
            update={"audit_trace_id": direct.audit_trace_id, "audit_trace": direct.audit_trace}
        )
        == direct
    )


def test_policy_evidence_is_local_and_controlled() -> None:
    client = BoundedMCPClient()
    evidence = client.call_tool(
        "policy-evidence",
        "get_evidence_for_pathway",
        {"pathway_code": "CANCER_2WW"},
    )

    assert evidence["demonstration_only"] is True
    assert evidence["validation_required"] is True
    assert evidence["evidence"]
    with pytest.raises(DomainValidationError):
        client.call_tool("policy-evidence", "get_evidence", {"evidence_id": "unknown"})
    with pytest.raises(MCPCapabilityError):
        client.read_resource("policy-evidence", "evidence://local/../secret")


def test_mcp_size_limits_call_limits_and_secret_redaction(monkeypatch: pytest.MonkeyPatch) -> None:
    client = BoundedMCPClient()

    with pytest.raises(MCPCapabilityError, match="input exceeds"):
        client.call_tool(
            "policy-evidence",
            "search_evidence",
            {"pathway_code": "CANCER_2WW", "query": "x" * 5000},
        )

    with pytest.raises(TypeError):
        client.call_tool(
            "case-data",
            "get_case",
            {"case_id": CASE_ID, "api_key": "secret-value"},
        )
    assert client.invocations[-1].invocation.input_summary["api_key"] == "<redacted>"

    limited = BoundedMCPClient()
    monkeypatch.setattr("mcp_servers.client.MAX_MCP_OUTPUT_CHARS", 1)
    with pytest.raises(MCPCapabilityError, match="output exceeds"):
        limited.call_tool("case-data", "list_cases", {})
    monkeypatch.undo()

    capped = BoundedMCPClient()
    for _ in range(MAX_CLIENT_CALLS):
        capped.call_tool("case-data", "get_case", {"case_id": CASE_ID})
    with pytest.raises(MCPCapabilityError, match="maximum MCP call limit"):
        capped.call_tool("case-data", "get_case", {"case_id": CASE_ID})


def test_mock_mcp_agent_workflow_preserves_deterministic_values() -> None:
    result = run_agent_assessment(CASE_ID, ExecutionMode.MOCK_MCP)
    direct = assess_case(get_case_by_id(CASE_ID))

    assert result.execution_mode == ExecutionMode.MOCK_MCP
    assert result.deterministic_assessment.risk_score == direct.risk_score
    assert result.deterministic_assessment.breach_status == direct.breach_status
    assert result.human_review_required is True
    assert any(invocation.tool_name.startswith("mcp:") for invocation in result.tool_invocations)
    assert any(
        invocation.tool_name == "mcp:policy-evidence.get_evidence_for_pathway"
        for invocation in result.tool_invocations
    )


def test_tool_access_matrix_preserves_least_privilege() -> None:
    assert TOOL_ACCESS_MATRIX["Escalation Agent"] == []
    assert TOOL_ACCESS_MATRIX["Review Agent"] == []
    assert "policy-evidence.get_evidence_for_pathway" in TOOL_ACCESS_MATRIX["Evidence Agent"]
