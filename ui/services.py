"""Testable UI service layer for synthetic demonstration actions."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from schemas.agent import AgentExecutionResult, ExecutionMode, LocalEvidenceDocument
from schemas.assessment import PathwayAssessment
from schemas.review import HumanReviewAmendment, HumanReviewDecision, HumanReviewRecord
from schemas.security import GuardrailResult
from services.agent_orchestrator import run_agent_assessment
from services.assessment_service import assess_case
from services.guardrail_service import GuardrailService
from services.human_review_service import HumanReviewService, ReviewStore
from services.security_utils import AMENDABLE_REVIEW_FIELDS, validate_safe_identifier
from tools.case_tools import get_case_by_id, load_synthetic_cases
from tools.evidence_tools import retrieve_local_evidence
from tools.exceptions import DomainValidationError

from ui.config import EVIDENCE_ROOT, PRIMARY_DEMO_CASE_ID, UIConfig
from ui.formatting import to_json_bytes


def list_case_options(presentation_mode: bool = False) -> list[dict[str, str]]:
    """Return selectable synthetic case rows."""
    cases = load_synthetic_cases()
    rows = [
        {
            "case_id": case.case_id,
            "pathway": case.pathway_code.value,
            "current_stage": case.current_stage,
            "priority": case.priority.value,
            "synthetic": str(case.synthetic),
        }
        for case in cases
        if case.synthetic
    ]
    if presentation_mode:
        return sorted(rows, key=lambda row: row["case_id"] != PRIMARY_DEMO_CASE_ID)
    return rows


def get_case_summary(case_id: str) -> dict[str, Any]:
    """Return safe case-display fields for a synthetic case."""
    validate_safe_identifier(case_id, "case_id")
    case = get_case_by_id(case_id)
    if not case.synthetic:
        raise DomainValidationError("only synthetic cases can be displayed")
    return case.model_dump(mode="json")


def run_deterministic(case_id: str) -> PathwayAssessment:
    """Run deterministic assessment for a selected synthetic case."""
    validate_safe_identifier(case_id, "case_id")
    return assess_case(get_case_by_id(case_id))


def run_agent(case_id: str, mode: ExecutionMode) -> AgentExecutionResult:
    """Run safe agent orchestration for a selected synthetic case."""
    if mode not in {ExecutionMode.MOCK, ExecutionMode.MOCK_MCP}:
        raise DomainValidationError("public UI supports only mock and mock-MCP modes by default")
    validate_safe_identifier(case_id, "case_id")
    return run_agent_assessment(case_id, mode)


def get_evidence(case_id: str, limit: int) -> list[LocalEvidenceDocument]:
    """Return controlled evidence for the case pathway."""
    case = get_case_by_id(case_id)
    return retrieve_local_evidence(case.pathway_code)[:limit]


def get_guardrail_result(
    assessment: PathwayAssessment, result: AgentExecutionResult | None = None
) -> GuardrailResult:
    """Return guardrail status for the deterministic or agent output."""
    service = GuardrailService()
    if result is not None:
        return service.check_draft(result.agent_draft, result.deterministic_assessment)
    return service.check_case_payload(assessment.model_dump(mode="json"))


def review_service(config: UIConfig) -> HumanReviewService:
    """Build a review service rooted at the configured runtime path."""
    return HumanReviewService(store=ReviewStore(config.review_store_path))


def prepare_review(case_id: str, mode: ExecutionMode, config: UIConfig) -> HumanReviewRecord:
    """Prepare a pending human-review record."""
    if mode not in {ExecutionMode.MOCK, ExecutionMode.MOCK_MCP}:
        raise DomainValidationError("review preparation requires safe mock execution mode")
    return review_service(config).prepare_review(case_id, mode)


def decide_review(
    review_id: str,
    decision: HumanReviewDecision,
    reviewer_alias: str,
    config: UIConfig,
    comments: str | None = None,
    reason: str | None = None,
    amendment_field: str | None = None,
    amendment_value: str | None = None,
) -> HumanReviewRecord:
    """Apply a safe demonstration review decision."""
    amendments: list[HumanReviewAmendment] = []
    if decision == HumanReviewDecision.AMEND:
        if amendment_field not in AMENDABLE_REVIEW_FIELDS:
            raise DomainValidationError("only approved narrative amendment fields are editable")
        amendments.append(HumanReviewAmendment(field=amendment_field, value=amendment_value or ""))
    return review_service(config).decide(
        review_id=review_id,
        decision=decision,
        reviewer_id=reviewer_alias,
        comments=comments,
        reason=reason,
        amendments=amendments,
    )


def verify_review(review_id: str, config: UIConfig) -> dict[str, object]:
    """Verify a review record by ID."""
    return review_service(config).verify_integrity(review_id)


def load_evaluation_evidence(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    """Load committed Milestone 6 evidence files."""
    allowed = root.resolve()
    if not allowed.exists() or root != EVIDENCE_ROOT:
        raise DomainValidationError("evaluation evidence must use committed milestone path")
    summary = (root / "evaluation-summary.md").read_text(encoding="utf-8")
    manifest = json.loads((root / "evaluation-manifest.json").read_text(encoding="utf-8"))
    benchmark = json.loads((root / "benchmark-summary.json").read_text(encoding="utf-8"))
    metric_rows: list[dict[str, str]] = []
    with (root / "metric-summary.csv").open(encoding="utf-8", newline="") as handle:
        metric_rows = list(csv.DictReader(handle))
    limitations = (root / "limitations.md").read_text(encoding="utf-8")
    return {
        "summary": summary,
        "manifest": manifest,
        "benchmark": benchmark,
        "metrics": metric_rows,
        "limitations": limitations,
    }


def build_download(payload: Any, label: str) -> bytes:
    """Build a safe JSON download."""
    return to_json_bytes(payload, label)
