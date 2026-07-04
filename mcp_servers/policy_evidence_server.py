"""Local Policy Evidence MCP server."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from schemas.case import PathwayCode
from tools.evidence_tools import (
    get_local_evidence_by_id,
    load_local_evidence,
    retrieve_local_evidence,
)

from mcp_servers.common import (
    create_server,
    validate_input_size,
    validate_no_path_traversal,
    with_metadata,
)

SERVER_NAME = "policy-evidence"


def list_evidence() -> dict[str, Any]:
    """Return all controlled local evidence records."""
    return with_metadata(
        {"evidence": [doc.model_dump(mode="json") for doc in load_local_evidence()]}
    )


def get_evidence(evidence_id: str) -> dict[str, Any]:
    """Return one controlled evidence record."""
    validate_no_path_traversal(evidence_id)
    return with_metadata(
        {"evidence": get_local_evidence_by_id(evidence_id).model_dump(mode="json")}
    )


def get_evidence_for_pathway(pathway_code: str) -> dict[str, Any]:
    """Return controlled evidence for one pathway."""
    return with_metadata(
        {
            "evidence": [
                doc.model_dump(mode="json")
                for doc in retrieve_local_evidence(PathwayCode(pathway_code))
            ]
        }
    )


def search_evidence(pathway_code: str, query: str = "") -> dict[str, Any]:
    """Search local evidence by pathway and optional text query."""
    validate_input_size({"pathway_code": pathway_code, "query": query})
    docs = retrieve_local_evidence(PathwayCode(pathway_code))
    if query:
        q = query.lower()
        docs = [doc for doc in docs if q in doc.title.lower() or q in doc.summary.lower()]
    return with_metadata({"evidence": [doc.model_dump(mode="json") for doc in docs]})


def read_evidence_resource(uri: str) -> dict[str, Any]:
    """Read a supported evidence resource URI."""
    if uri == "evidence://local/index":
        return list_evidence()
    pathway_prefix = "evidence://local/pathway/"
    if uri.startswith(pathway_prefix):
        return get_evidence_for_pathway(uri.removeprefix(pathway_prefix))
    evidence_prefix = "evidence://local/"
    if uri.startswith(evidence_prefix):
        evidence_id = uri.removeprefix(evidence_prefix)
        validate_no_path_traversal(evidence_id)
        return get_evidence(evidence_id)
    raise ValueError(f"unsupported evidence resource: {uri}")


def create_policy_evidence_server() -> FastMCP:
    """Create the local Policy Evidence FastMCP server."""
    server = create_server(SERVER_NAME, "Controlled local demonstration evidence only.")
    server.tool()(search_evidence)
    server.tool()(get_evidence)
    server.tool()(list_evidence)
    server.tool()(get_evidence_for_pathway)

    @server.resource("evidence://local/index")
    def evidence_index_resource() -> str:
        return str(list_evidence())

    @server.resource("evidence://local/{evidence_id}")
    def evidence_resource(evidence_id: str) -> str:
        return str(get_evidence(evidence_id))

    @server.resource("evidence://local/pathway/{pathway_code}")
    def pathway_evidence_resource(pathway_code: str) -> str:
        return str(get_evidence_for_pathway(pathway_code))

    return server


if __name__ == "__main__":
    create_policy_evidence_server().run(transport="stdio")
