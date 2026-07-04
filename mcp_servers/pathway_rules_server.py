"""Local Pathway Rules MCP server."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from mcp.server.fastmcp import FastMCP
from schemas.case import PathwayCode, TargetUnit
from services.assessment_service import assess_case
from tools.case_tools import get_case_by_id
from tools.pathway_tools import (
    calculate_elapsed_time as deterministic_elapsed_time,
)
from tools.pathway_tools import (
    determine_breach_status as deterministic_breach_status,
)
from tools.pathway_tools import (
    get_pathway_rule as deterministic_get_pathway_rule,
)
from tools.pathway_tools import (
    load_pathway_rules,
)

from mcp_servers.common import (
    create_server,
    validate_input_size,
    validate_no_path_traversal,
    with_metadata,
)

SERVER_NAME = "pathway-rules"


def get_pathway_rule(pathway_code: str) -> dict[str, Any]:
    """Return a controlled pathway rule."""
    validate_no_path_traversal(pathway_code)
    rule = deterministic_get_pathway_rule(PathwayCode(pathway_code))
    _, rules = load_pathway_rules()
    return with_metadata({"rule": rule.model_dump(mode="json"), "rule_count": len(rules)})


def list_pathway_rules() -> dict[str, Any]:
    """Return all controlled pathway rules."""
    rule_version, rules = load_pathway_rules()
    return with_metadata(
        {"rule_version": rule_version, "rules": [r.model_dump(mode="json") for r in rules]}
    )


def calculate_elapsed_time(
    start_datetime: str, end_datetime: str, target_unit: str
) -> dict[str, Any]:
    """Calculate elapsed time through deterministic pathway tools."""
    validate_input_size({"start": start_datetime, "end": end_datetime, "unit": target_unit})
    elapsed = deterministic_elapsed_time(
        datetime.fromisoformat(start_datetime),
        datetime.fromisoformat(end_datetime),
        TargetUnit(target_unit),
    )
    return with_metadata({"elapsed_time": elapsed.model_dump(mode="json")})


def determine_breach_status(target_consumption_percent: float, pathway_code: str) -> dict[str, Any]:
    """Classify breach status using controlled pathway rule thresholds."""
    rule = deterministic_get_pathway_rule(PathwayCode(pathway_code))
    status = deterministic_breach_status(target_consumption_percent, rule)
    return with_metadata({"breach_status": status.value})


def run_pathway_assessment(case_id: str) -> dict[str, Any]:
    """Run the authoritative deterministic pathway assessment."""
    validate_no_path_traversal(case_id)
    assessment = assess_case(get_case_by_id(case_id))
    return with_metadata({"assessment": assessment.model_dump(mode="json")})


def read_pathway_resource(uri: str) -> dict[str, Any]:
    """Read a supported pathway resource URI."""
    if uri == "pathway://rules/index":
        return list_pathway_rules()
    prefix = "pathway://rules/"
    if uri.startswith(prefix):
        code = uri.removeprefix(prefix)
        validate_no_path_traversal(code)
        return get_pathway_rule(code)
    raise ValueError(f"unsupported pathway resource: {uri}")


def create_pathway_rules_server() -> FastMCP:
    """Create the local Pathway Rules FastMCP server."""
    server = create_server(SERVER_NAME, "Controlled pathway rules and deterministic calculations.")
    server.tool()(get_pathway_rule)
    server.tool()(list_pathway_rules)
    server.tool()(calculate_elapsed_time)
    server.tool()(determine_breach_status)
    server.tool()(run_pathway_assessment)

    @server.resource("pathway://rules/index")
    def pathway_index_resource() -> str:
        return str(list_pathway_rules())

    @server.resource("pathway://rules/{pathway_code}")
    def pathway_rule_resource(pathway_code: str) -> str:
        return str(get_pathway_rule(pathway_code))

    return server


if __name__ == "__main__":
    create_pathway_rules_server().run(transport="stdio")
