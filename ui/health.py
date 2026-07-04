"""Headless health checks for the demonstration UI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mcp_servers.registry import list_server_definitions
from schemas.agent import ExecutionMode
from services.skill_executor import list_skill_definitions
from tools.case_tools import load_synthetic_cases
from tools.exceptions import DomainValidationError
from tools.pathway_tools import load_pathway_rules

from ui.config import SAFETY_BANNER, UIConfig
from ui.services import load_evaluation_evidence, prepare_review, run_agent, run_deterministic


def run_health_checks(config: UIConfig) -> dict[str, Any]:
    """Run safe local health checks for UI and deployment readiness."""
    cases = load_synthetic_cases()
    if not cases:
        raise DomainValidationError("synthetic cases did not load")
    _, rules = load_pathway_rules()
    if len(rules) != 5:
        raise DomainValidationError("expected five demonstration pathway rules")
    if len(list_server_definitions()) != 3:
        raise DomainValidationError("expected three local MCP server definitions")
    if len(list_skill_definitions()) != 4:
        raise DomainValidationError("expected four approved Agent Skills")
    case_id = cases[0].case_id
    assessment = run_deterministic(case_id)
    agent = run_agent(case_id, ExecutionMode.MOCK_MCP)
    evidence = load_evaluation_evidence()
    config.review_store_path.mkdir(parents=True, exist_ok=True)
    if not config.review_store_path.exists():
        raise DomainValidationError("review store cannot be initialised")
    return {
        "status": "healthy",
        "case_id": case_id,
        "assessment_case_id": assessment.case_id,
        "agent_execution_mode": agent.execution_mode.value,
        "mcp_default_works": agent.execution_mode == ExecutionMode.MOCK_MCP,
        "evaluation_run_id": evidence["benchmark"]["run_id"],
        "review_store_writable": _path_writable(config.review_store_path),
        "safety_banner_present": bool(SAFETY_BANNER),
        "live_mode_enabled": config.enable_live_mode,
        "demonstration_only": True,
    }


def _path_writable(path: Path) -> bool:
    probe = path / ".healthcheck"
    probe.write_text("ok\n", encoding="utf-8")
    probe.unlink()
    return True


def prepare_review_health_check(config: UIConfig) -> dict[str, Any]:
    """Optionally verify review creation in the configured store."""
    record = prepare_review("SYN-CANCER-2WW-001", ExecutionMode.MOCK_MCP, config)
    return {
        "review_id": record.review_id,
        "status": record.status.value,
        "submitted": record.submitted,
        "authenticated_identity": record.authenticated_identity,
    }
