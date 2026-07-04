"""Local Case Data MCP server."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from schemas.case import PathwayCode
from tools.case_tools import (
    detect_prohibited_identity_fields,
    get_case_by_id,
    list_cases_by_pathway,
    load_synthetic_cases,
    validate_synthetic_case,
)

from mcp_servers.common import (
    create_server,
    validate_input_size,
    validate_no_path_traversal,
    with_metadata,
)

SERVER_NAME = "case-data"


def get_case(case_id: str) -> dict[str, Any]:
    """Return one validated synthetic case."""
    validate_input_size(case_id)
    validate_no_path_traversal(case_id)
    case = get_case_by_id(case_id)
    return with_metadata({"case": case.model_dump(mode="json")})


def list_cases() -> dict[str, Any]:
    """Return an index of synthetic cases."""
    cases = load_synthetic_cases()
    return with_metadata(
        {
            "cases": [
                {"case_id": case.case_id, "pathway_code": case.pathway_code.value} for case in cases
            ]
        }
    )


def list_cases_by_pathway_tool(pathway_code: str) -> dict[str, Any]:
    """Return cases for a supported pathway."""
    code = PathwayCode(pathway_code)
    return with_metadata(
        {"cases": [case.model_dump(mode="json") for case in list_cases_by_pathway(code)]}
    )


def validate_case(case_payload: dict[str, Any]) -> dict[str, Any]:
    """Validate a raw synthetic case payload."""
    validate_input_size(case_payload)
    prohibited = detect_prohibited_identity_fields(case_payload)
    if prohibited:
        raise ValueError(f"prohibited identity fields: {sorted(prohibited)}")
    case = validate_synthetic_case(case_payload)
    return with_metadata({"valid": True, "case_id": case.case_id})


def read_case_resource(uri: str) -> dict[str, Any]:
    """Read a supported case resource URI."""
    safe_uri = uri.replace("case://synthetic/", "").replace("case://synthetic/index", "index")
    validate_no_path_traversal(safe_uri)
    if uri == "case://synthetic/index":
        return list_cases()
    prefix = "case://synthetic/"
    if uri.startswith(prefix):
        return get_case(uri.removeprefix(prefix))
    raise ValueError(f"unsupported case resource: {uri}")


def create_case_data_server() -> FastMCP:
    """Create the local Case Data FastMCP server."""
    server = create_server(SERVER_NAME, "Synthetic case data only; no arbitrary file access.")
    server.tool()(get_case)
    server.tool(name="list_cases")(list_cases)
    server.tool(name="list_cases_by_pathway")(list_cases_by_pathway_tool)
    server.tool()(validate_case)

    @server.resource("case://synthetic/index")
    def case_index_resource() -> str:
        return str(list_cases())

    @server.resource("case://synthetic/{case_id}")
    def case_resource(case_id: str) -> str:
        return str(get_case(case_id))

    return server


if __name__ == "__main__":
    create_case_data_server().run(transport="stdio")
