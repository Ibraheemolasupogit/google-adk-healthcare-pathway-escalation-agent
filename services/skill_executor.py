"""Approved local Agent Skill registry and execution service."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypeVar
from uuid import uuid4

from mcp_servers.client import BoundedMCPClient
from schemas.agent import ExecutionMode
from schemas.mcp import (
    SkillDefinition,
    SkillExecutionRequest,
    SkillExecutionResult,
    SkillExecutionStep,
    SkillValidationResult,
)
from tools.exceptions import DomainValidationError

from services.agent_orchestrator import run_agent_assessment

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = PROJECT_ROOT / "skills"
APPROVED_SKILLS = {
    "identify_pathway",
    "calculate_risk",
    "retrieve_evidence",
    "generate_escalation",
}
MAX_SKILL_STEPS = 8
T = TypeVar("T")


class SkillRegistry:
    """Registry that loads only approved local skills."""

    def list_skills(self) -> list[SkillDefinition]:
        """Return all approved skill definitions."""
        return [self.get_skill(name) for name in sorted(APPROVED_SKILLS)]

    def get_skill(self, name: str) -> SkillDefinition:
        """Return one approved skill definition."""
        if name not in APPROVED_SKILLS:
            raise DomainValidationError(f"unknown skill: {name}")
        metadata_path = SKILLS_ROOT / name / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        return SkillDefinition.model_validate(metadata)


class SkillExecutor:
    """Execute approved skills through deterministic or MCP capabilities."""

    def __init__(self, client: BoundedMCPClient | None = None) -> None:
        self.client = client or BoundedMCPClient()
        self.registry = SkillRegistry()
        self.steps: list[SkillExecutionStep] = []

    def execute(self, skill_name: str, case_id: str) -> SkillExecutionResult:
        """Execute one approved skill for a synthetic case."""
        definition = self.registry.get_skill(skill_name)
        request = SkillExecutionRequest(
            request_id=f"SKILL-{uuid4()}",
            skill_name=skill_name,
            case_id=case_id,
            execution_mode=ExecutionMode.MOCK_MCP,
        )
        output = self._run_skill(skill_name, case_id)
        validation = SkillValidationResult(valid=True, findings=[])
        return SkillExecutionResult(
            request_id=request.request_id,
            execution_mode=request.execution_mode,
            skill_name=skill_name,
            skill_version=definition.version,
            case_id=case_id,
            output=output,
            steps=self.steps,
            mcp_invocations=self.client.invocations,
            validation=validation,
            warnings=["Skill execution uses demonstration-only local data."],
            demonstration_only=True,
            human_review_required=True,
            success=True,
        )

    def _run_skill(self, skill_name: str, case_id: str) -> dict[str, Any]:
        if skill_name == "identify_pathway":
            case = self._step(
                "validate synthetic case",
                lambda: self.client.call_tool(
                    "case-data",
                    "get_case",
                    {"case_id": case_id},
                ),
            )
            pathway_code = case["case"]["pathway_code"]
            rule = self._step(
                "retrieve pathway rule",
                lambda: self.client.call_tool(
                    "pathway-rules",
                    "get_pathway_rule",
                    {"pathway_code": pathway_code},
                ),
            )
            return {
                "case_id": case_id,
                "pathway_code": pathway_code,
                "pathway_name": rule["rule"]["pathway_name"],
                "target": rule["rule"]["target_value"],
                "target_unit": rule["rule"]["target_unit"],
                "rule_metadata": rule["rule"],
                "demonstration_only": True,
                "warnings": [rule["warning"]],
            }
        if skill_name == "calculate_risk":
            assessment = self._step(
                "run deterministic assessment",
                lambda: self.client.call_tool(
                    "pathway-rules",
                    "run_pathway_assessment",
                    {"case_id": case_id},
                ),
            )["assessment"]
            return {
                "case_id": case_id,
                "breach_status": assessment["breach_status"],
                "target_consumption": assessment["target_consumption_percent"],
                "variance": assessment["variance_from_target"],
                "risk_score": assessment["risk_score"],
                "risk_level": assessment["risk_level"],
                "risk_factors": assessment["risk_factors"],
                "audit_trace_id": assessment["audit_trace_id"],
                "human_review_required": True,
            }
        if skill_name == "retrieve_evidence":
            case = self._step(
                "validate synthetic case",
                lambda: self.client.call_tool(
                    "case-data",
                    "get_case",
                    {"case_id": case_id},
                ),
            )["case"]
            evidence = self._step(
                "retrieve local evidence",
                lambda: self.client.call_tool(
                    "policy-evidence",
                    "get_evidence_for_pathway",
                    {"pathway_code": case["pathway_code"]},
                ),
            )["evidence"]
            return {
                "case_id": case_id,
                "evidence": evidence,
                "demonstration_only": True,
                "warnings": ["Evidence is demonstration-only and validation-required."],
            }
        if skill_name == "generate_escalation":
            result = self._step(
                "generate mock-mcp escalation",
                lambda: run_agent_assessment(case_id, ExecutionMode.MOCK_MCP).model_dump(
                    mode="json"
                ),
            )
            return {
                "case_id": case_id,
                "sections": result["agent_draft"]["sections"],
                "human_review_required": True,
                "review_status": result["review_status"],
                "demonstration_only": True,
                "submitted": False,
            }
        raise DomainValidationError(f"unknown skill: {skill_name}")

    def _step(self, description: str, func: Callable[[], T]) -> T:
        if len(self.steps) >= MAX_SKILL_STEPS:
            raise DomainValidationError("maximum skill step limit exceeded")
        started = datetime.now(UTC)
        try:
            output = func()
            success = True
            return output
        finally:
            self.steps.append(
                SkillExecutionStep(
                    sequence=len(self.steps) + 1,
                    skill_name="local",
                    description=description,
                    started_at=started,
                    completed_at=datetime.now(UTC),
                    success=success if "success" in locals() else False,
                )
            )


def list_skill_definitions() -> list[SkillDefinition]:
    """Return approved skill definitions."""
    return SkillRegistry().list_skills()


def execute_skill(skill_name: str, case_id: str) -> SkillExecutionResult:
    """Execute an approved local skill."""
    return SkillExecutor().execute(skill_name, case_id)
