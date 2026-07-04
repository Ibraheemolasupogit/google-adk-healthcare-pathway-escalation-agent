"""Central deterministic guardrail pipeline for Milestone 5."""

from __future__ import annotations

import re
from typing import Any

from pydantic import ValidationError
from schemas.agent import AgentDraft, LocalEvidenceDocument
from schemas.assessment import PathwayAssessment
from schemas.review import HumanReviewRecord, HumanReviewStatus
from schemas.security import GuardrailCategory, GuardrailFinding, GuardrailResult, GuardrailSeverity
from tools.case_tools import detect_prohibited_identity_fields

from services.security_utils import (
    MAX_EVIDENCE_SUMMARY_CHARS,
    MAX_GUARDRAIL_TEXT_CHARS,
    contains_path_traversal,
    extract_deterministic_values,
    redact_secrets,
    sha256_hash,
)

PROMPT_INJECTION_PATTERNS = [
    r"ignore (?:all )?(?:previous|prior) instructions",
    r"reveal (?:the )?system prompt",
    r"show (?:the )?system prompt",
    r"expose hidden reasoning",
    r"chain of thought",
    r"change (?:the )?risk score",
    r"mark (?:this|it|output) as approved",
    r"mark (?:this|it|output) approved",
    r"bypass human review",
    r"approve again",
    r"execute arbitrary commands?",
    r"read arbitrary files?",
    r"use a different target",
    r"access (?:live )?nhs systems?",
]
CLINICAL_PATTERNS = [
    r"\bdiagnose\b",
    r"\bprescribe\b",
    r"\bmedication\b",
    r"\btreatment plan\b",
    r"\bclinically safe\b",
    r"\bclinically approved\b",
    r"\bmedically cleared\b",
    r"\bpatient should receive\b",
    r"\balter clinical priority\b",
    r"\bdischarge the patient\b",
    r"\bemergency diagnosis\b",
]
AUTONOMOUS_ACTION_PATTERNS = [
    r"escalation has been submitted",
    r"case has been sent",
    r"patient has been prioritised",
    r"appointment has been changed",
    r"referral has been approved",
    r"action completed automatically",
]
PERSONAL_DATA_PATTERNS = [
    r"\bnhs(?:\s|-)?number\b",
    r"\b\d{3}\s?\d{3}\s?\d{4}\b",
    r"\bdate of birth\b",
    r"\bdob\b",
    r"\bpatient name\b",
    r"\bhospital number\b",
    r"\b(?:telephone|phone)\b",
    r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b",
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
]
UNSUPPORTED_CLAIM_PATTERNS = [
    r"\bauthoritative nhs integration\b",
    r"\bconnected to live nhs\b",
    r"\breal patient\b",
    r"\bclinically approved\b",
    r"\boperationally approved\b",
]


class GuardrailService:
    """Run deterministic guardrail checks without model judgement."""

    def check_text(self, text: str, field: str = "text") -> GuardrailResult:
        """Validate user or generated text."""
        findings: list[GuardrailFinding] = []
        redacted = redact_secrets(text)
        if len(text) > MAX_GUARDRAIL_TEXT_CHARS:
            findings.append(
                _finding(GuardrailCategory.OVERSIZED_INPUT, "input exceeds size limit", field)
            )
        if contains_path_traversal(text):
            findings.append(
                _finding(
                    GuardrailCategory.PATH_TRAVERSAL,
                    "path traversal marker detected",
                    field,
                )
            )
        findings.extend(
            _match_findings(
                text, PROMPT_INJECTION_PATTERNS, GuardrailCategory.PROMPT_INJECTION, field
            )
        )
        findings.extend(
            _match_findings(text, CLINICAL_PATTERNS, GuardrailCategory.CLINICAL_ADVICE, field)
        )
        findings.extend(
            _match_findings(
                text, AUTONOMOUS_ACTION_PATTERNS, GuardrailCategory.AUTONOMOUS_ACTION, field
            )
        )
        findings.extend(
            _match_findings(text, PERSONAL_DATA_PATTERNS, GuardrailCategory.PERSONAL_DATA, field)
        )
        findings.extend(
            _match_findings(
                text, UNSUPPORTED_CLAIM_PATTERNS, GuardrailCategory.UNSUPPORTED_CLAIM, field
            )
        )
        if redacted != text:
            findings.append(
                _finding(GuardrailCategory.SECRET_EXPOSURE, "secret-like value redacted", field)
            )
        return _result(findings, redacted)

    def check_case_payload(self, payload: dict[str, Any]) -> GuardrailResult:
        """Validate a synthetic case payload for identity and malformed content."""
        findings: list[GuardrailFinding] = []
        prohibited = detect_prohibited_identity_fields(payload)
        for field in sorted(prohibited):
            findings.append(
                _finding(
                    GuardrailCategory.PERSONAL_DATA,
                    f"prohibited identity field: {field}",
                    field,
                )
            )
        findings.extend(self.check_text(str(payload), "case_payload").findings)
        return _result(findings, redact_secrets(str(payload)))

    def check_evidence(self, evidence: LocalEvidenceDocument | dict[str, Any]) -> GuardrailResult:
        """Validate untrusted local evidence boundaries."""
        findings: list[GuardrailFinding] = []
        try:
            doc = (
                evidence
                if isinstance(evidence, LocalEvidenceDocument)
                else LocalEvidenceDocument.model_validate(evidence)
            )
        except ValidationError as exc:
            findings.append(
                _finding(
                    GuardrailCategory.MALFORMED_OUTPUT,
                    f"malformed evidence: {exc}",
                    "evidence",
                )
            )
            return _result(findings, None)
        if not doc.demonstration_only or not doc.validation_required:
            findings.append(
                _finding(
                    GuardrailCategory.EVIDENCE_INJECTION,
                    "evidence must be demonstration-only and validation-required",
                    "evidence",
                )
            )
        if not doc.source_label:
            findings.append(
                _finding(
                    GuardrailCategory.MALFORMED_OUTPUT,
                    "missing source label",
                    "source_label",
                )
            )
        if len(doc.summary) > MAX_EVIDENCE_SUMMARY_CHARS:
            findings.append(
                _finding(
                    GuardrailCategory.OVERSIZED_INPUT,
                    "evidence summary too long",
                    "summary",
                )
            )
        text_result = self.check_text(f"{doc.title}\n{doc.summary}", "evidence")
        for finding in text_result.findings:
            category = (
                GuardrailCategory.EVIDENCE_INJECTION
                if finding.category
                in {GuardrailCategory.PROMPT_INJECTION, GuardrailCategory.DETERMINISTIC_OVERRIDE}
                else finding.category
            )
            findings.append(finding.model_copy(update={"category": category}))
        return _result(findings, text_result.redacted_text)

    def check_draft(
        self, draft: AgentDraft | dict[str, Any], assessment: PathwayAssessment | dict[str, Any]
    ) -> GuardrailResult:
        """Validate an agent draft against deterministic assessment values."""
        findings: list[GuardrailFinding] = []
        try:
            draft_model = (
                draft if isinstance(draft, AgentDraft) else AgentDraft.model_validate(draft)
            )
            assessment_model = (
                assessment
                if isinstance(assessment, PathwayAssessment)
                else PathwayAssessment.model_validate(assessment)
            )
        except ValidationError as exc:
            findings.append(_finding(GuardrailCategory.MALFORMED_OUTPUT, str(exc), "draft"))
            return _result(findings, None)
        assessment_values = extract_deterministic_values(assessment_model.model_dump(mode="json"))
        draft_values = draft_model.deterministic_values
        expected = {
            "breach_status": assessment_values["breach_status"],
            "risk_score": assessment_values["risk_score"],
            "risk_level": assessment_values["risk_level"],
            "target_value": assessment_values["target"]["value"],
            "elapsed_value": assessment_values["elapsed_time"]["value"],
        }
        for key, value in expected.items():
            if draft_values.get(key) != value:
                findings.append(
                    _finding(
                        GuardrailCategory.DETERMINISTIC_OVERRIDE,
                        f"draft deterministic value changed: {key}",
                        key,
                    )
                )
        for name, text in draft_model.sections.items():
            findings.extend(self.check_text(text, f"sections.{name}").findings)
        for doc in draft_model.evidence:
            findings.extend(self.check_evidence(doc).findings)
        if draft_model.review_status.value != "PENDING":
            findings.append(
                _finding(
                    GuardrailCategory.REVIEW_BYPASS,
                    "draft review status is not pending",
                    "review_status",
                )
            )
        return _result(findings, None)

    def check_review_state(self, record: HumanReviewRecord) -> GuardrailResult:
        """Validate backend review state invariants."""
        findings: list[GuardrailFinding] = []
        if record.status not in set(HumanReviewStatus):
            findings.append(
                _finding(
                    GuardrailCategory.INVALID_STATE_TRANSITION,
                    "unknown review state",
                    "status",
                )
            )
        if record.submitted:
            findings.append(
                _finding(
                    GuardrailCategory.AUTONOMOUS_ACTION,
                    "review record claims submission",
                    "submitted",
                )
            )
        if record.authenticated_identity:
            findings.append(
                _finding(
                    GuardrailCategory.UNSUPPORTED_CLAIM,
                    "review record claims authentication",
                    "authenticated_identity",
                )
            )
        if record.draft_hash != sha256_hash(record.draft):
            findings.append(
                _finding(
                    GuardrailCategory.DETERMINISTIC_OVERRIDE,
                    "draft hash mismatch",
                    "draft_hash",
                )
            )
        if record.deterministic_assessment_hash != sha256_hash(record.deterministic_assessment):
            findings.append(
                _finding(
                    GuardrailCategory.DETERMINISTIC_OVERRIDE,
                    "deterministic assessment hash mismatch",
                    "deterministic_assessment_hash",
                )
            )
        return _result(findings, None)


def _match_findings(
    text: str, patterns: list[str], category: GuardrailCategory, field: str
) -> list[GuardrailFinding]:
    findings: list[GuardrailFinding] = []
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            actual_category = _specific_category(category, match.group(0))
            findings.append(
                _finding(
                    actual_category,
                    f"{actual_category.value} pattern detected",
                    field,
                    match.group(0),
                )
            )
    return findings


def _specific_category(category: GuardrailCategory, matched: str) -> GuardrailCategory:
    value = matched.lower()
    if category == GuardrailCategory.PROMPT_INJECTION:
        if "risk score" in value or "target" in value:
            return GuardrailCategory.DETERMINISTIC_OVERRIDE
        if "approved" in value or "approve" in value or "human review" in value:
            return GuardrailCategory.REVIEW_BYPASS
        if "command" in value or "file" in value:
            return GuardrailCategory.TOOL_MISUSE
    return category


def _finding(
    category: GuardrailCategory,
    message: str,
    field: str | None = None,
    matched_text: str | None = None,
) -> GuardrailFinding:
    return GuardrailFinding(
        category=category,
        severity=GuardrailSeverity.BLOCKING,
        message=message,
        field=field,
        matched_text=matched_text,
    )


def _result(findings: list[GuardrailFinding], redacted_text: str | None) -> GuardrailResult:
    blocking = any(finding.severity == GuardrailSeverity.BLOCKING for finding in findings)
    return GuardrailResult(
        passed=not blocking,
        safe_for_human_review=not blocking,
        findings=findings,
        redacted_text=redacted_text,
    )


def guardrail_service() -> GuardrailService:
    """Return a guardrail service instance."""
    return GuardrailService()
