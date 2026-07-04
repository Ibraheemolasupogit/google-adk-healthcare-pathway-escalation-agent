"""Structured safety review for Milestone 3 agent drafts."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError
from schemas.agent import AgentDraft, ReviewFinding, ReviewResult, ReviewSeverity
from schemas.assessment import PathwayAssessment, ReviewStatus

PROHIBITED_CLINICAL_TERMS = {
    "diagnose",
    "diagnosis",
    "medication",
    "prescribe",
    "treatment recommendation",
    "clinical prioritisation",
    "clinically approved",
}


def review_agent_draft(
    draft_payload: dict[str, Any],
    deterministic_assessment: PathwayAssessment,
) -> ReviewResult:
    """Validate a draft against deterministic values and safety constraints."""
    findings: list[ReviewFinding] = []
    try:
        draft = AgentDraft.model_validate(draft_payload)
    except ValidationError as exc:
        return ReviewResult(
            safe_for_human_review=False,
            findings=[
                ReviewFinding(
                    finding_code="SCHEMA_VALIDATION_FAILED",
                    severity=ReviewSeverity.ERROR,
                    message=str(exc),
                )
            ],
            validation_passed=False,
            prohibited_language_detected=False,
            unsupported_claims_detected=True,
            review_status=ReviewStatus.PENDING,
        )

    _check_required_sections(draft, findings)
    _check_deterministic_values(draft, deterministic_assessment, findings)
    prohibited = _detect_prohibited_language(draft)
    if prohibited:
        findings.append(
            ReviewFinding(
                finding_code="PROHIBITED_CLINICAL_LANGUAGE",
                severity=ReviewSeverity.ERROR,
                message=f"Prohibited clinical language detected: {sorted(prohibited)}",
            )
        )
    if draft.unsupported_claims:
        findings.append(
            ReviewFinding(
                finding_code="UNSUPPORTED_CLAIMS",
                severity=ReviewSeverity.ERROR,
                message="Draft contains unsupported claims.",
                field="unsupported_claims",
            )
        )
    if not draft.human_review_required or draft.review_status != ReviewStatus.PENDING:
        findings.append(
            ReviewFinding(
                finding_code="HUMAN_REVIEW_NOT_ENFORCED",
                severity=ReviewSeverity.ERROR,
                message="Draft must require human review and remain pending.",
            )
        )

    has_error = any(finding.severity == ReviewSeverity.ERROR for finding in findings)
    return ReviewResult(
        safe_for_human_review=not has_error,
        findings=findings
        or [
            ReviewFinding(
                finding_code="SAFE_FOR_HUMAN_REVIEW",
                severity=ReviewSeverity.INFO,
                message="Draft is safe to present to an authorised human reviewer.",
            )
        ],
        validation_passed=not has_error,
        prohibited_language_detected=bool(prohibited),
        unsupported_claims_detected=bool(draft.unsupported_claims),
        review_status=ReviewStatus.PENDING,
    )


def _check_required_sections(draft: AgentDraft, findings: list[ReviewFinding]) -> None:
    required_sections = {
        "Case Summary",
        "Pathway Status",
        "Operational Risk",
        "Deterministic Risk Factors",
        "Supporting Demonstration Evidence",
        "Recommended Operational Actions",
        "Assumptions",
        "Warnings",
        "Human Review Status",
        "Audit Trace",
    }
    missing = required_sections.difference(draft.sections)
    if missing:
        findings.append(
            ReviewFinding(
                finding_code="MISSING_DRAFT_SECTIONS",
                severity=ReviewSeverity.ERROR,
                message=f"Missing required sections: {sorted(missing)}",
                field="sections",
            )
        )


def _check_deterministic_values(
    draft: AgentDraft,
    assessment: PathwayAssessment,
    findings: list[ReviewFinding],
) -> None:
    expected_values = {
        "breach_status": assessment.breach_status.value,
        "risk_score": assessment.risk_score,
        "risk_level": assessment.risk_level.value,
        "target_value": assessment.target.value,
        "elapsed_value": assessment.elapsed_time.value,
    }
    for key, expected in expected_values.items():
        if draft.deterministic_values.get(key) != expected:
            findings.append(
                ReviewFinding(
                    finding_code="DETERMINISTIC_VALUE_OVERRIDE",
                    severity=ReviewSeverity.ERROR,
                    message=f"{key} does not match deterministic source of truth.",
                    field=f"deterministic_values.{key}",
                )
            )


def _detect_prohibited_language(draft: AgentDraft) -> set[str]:
    text = " ".join(draft.sections.values()).lower()
    return {term for term in PROHIBITED_CLINICAL_TERMS if term in text}
