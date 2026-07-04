"""Safe ADK tool wrappers around deterministic Milestone 2 services."""

from __future__ import annotations

from typing import Any

from google.adk.tools.function_tool import FunctionTool
from schemas.assessment import PathwayAssessment
from schemas.case import PathwayCode
from services.assessment_service import assess_case

from tools.case_tools import get_case_by_id
from tools.evidence_tools import retrieve_local_evidence
from tools.pathway_tools import get_pathway_rule


def get_synthetic_case(case_id: str) -> dict[str, Any]:
    """Return a validated synthetic case by ID."""
    return get_case_by_id(case_id).model_dump(mode="json")


def get_pathway_rule_tool(pathway_code: str) -> dict[str, Any]:
    """Return the controlled demonstration pathway rule for a pathway code."""
    return get_pathway_rule(PathwayCode(pathway_code)).model_dump(mode="json")


def run_deterministic_assessment(case_id: str) -> dict[str, Any]:
    """Run the deterministic assessment engine for a synthetic case ID."""
    return assess_case(get_case_by_id(case_id)).model_dump(mode="json")


def get_risk_factors(case_id: str) -> list[dict[str, Any]]:
    """Return deterministic risk factors for a synthetic case ID."""
    assessment = assess_case(get_case_by_id(case_id))
    return [factor.model_dump(mode="json") for factor in assessment.risk_factors]


def get_recommended_actions(case_id: str) -> list[dict[str, Any]]:
    """Return deterministic non-clinical recommended actions for a case ID."""
    assessment = assess_case(get_case_by_id(case_id))
    return [action.model_dump(mode="json") for action in assessment.recommended_actions]


def get_audit_trace(case_id: str) -> dict[str, Any]:
    """Return the deterministic audit trace for a synthetic case ID."""
    return assess_case(get_case_by_id(case_id)).audit_trace.model_dump(mode="json")


def retrieve_local_evidence_tool(pathway_code: str) -> list[dict[str, Any]]:
    """Return controlled local demonstration evidence for a pathway code."""
    return [
        doc.model_dump(mode="json") for doc in retrieve_local_evidence(PathwayCode(pathway_code))
    ]


def validate_escalation_output_tool(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate that an assessment-like payload preserves human review controls."""
    assessment = PathwayAssessment.model_validate(payload)
    return {
        "case_id": assessment.case_id,
        "human_review_required": assessment.human_review_required,
        "review_status": assessment.review_status.value,
        "audit_trace_id": assessment.audit_trace_id,
    }


def build_adk_tools() -> list[Any]:
    """Build ADK FunctionTool wrappers for controlled local tools."""
    return [
        FunctionTool(get_synthetic_case),
        FunctionTool(get_pathway_rule_tool),
        FunctionTool(run_deterministic_assessment),
        FunctionTool(get_risk_factors),
        FunctionTool(get_recommended_actions),
        FunctionTool(get_audit_trace),
        FunctionTool(retrieve_local_evidence_tool),
        FunctionTool(validate_escalation_output_tool),
    ]
