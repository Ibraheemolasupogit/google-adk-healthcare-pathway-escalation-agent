"""Backend-only human-review workflow for synthetic demonstration outputs."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from schemas.agent import AgentExecutionResult, ExecutionMode
from schemas.review import (
    HumanReviewAmendment,
    HumanReviewDecision,
    HumanReviewRecord,
    HumanReviewStatus,
    ReviewHistoryEntry,
    ReviewIntegrityMetadata,
)
from schemas.security import GuardrailCategory, GuardrailFinding, GuardrailSeverity
from tools.exceptions import DomainValidationError

from services.agent_orchestrator import run_agent_assessment
from services.guardrail_service import GuardrailService
from services.security_utils import (
    sha256_hash,
    validate_amendment_field,
    validate_safe_identifier,
)

DEFAULT_REVIEW_DIR = Path("artifacts") / "reviews"


class ReviewStore:
    """Local JSON review store with safe filenames and atomic writes."""

    def __init__(self, root: Path = DEFAULT_REVIEW_DIR) -> None:
        self.root = root

    def path_for(self, review_id: str) -> Path:
        """Return a safe path for a review ID."""
        validate_safe_identifier(review_id, "review_id")
        return self.root / f"{review_id}.json"

    def save(self, record: HumanReviewRecord) -> None:
        """Atomically write a review record."""
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.path_for(record.review_id)
        tmp_path = path.with_suffix(".json.tmp")
        payload = record.model_dump(mode="json")
        tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(tmp_path, path)

    def load(self, review_id: str) -> HumanReviewRecord:
        """Load and validate a review record."""
        path = self.path_for(review_id)
        payload = json.loads(path.read_text(encoding="utf-8"))
        return HumanReviewRecord.model_validate(payload)

    def list_records(self) -> list[HumanReviewRecord]:
        """Return stored review records in deterministic order."""
        if not self.root.exists():
            return []
        records: list[HumanReviewRecord] = []
        for path in sorted(self.root.glob("*.json")):
            records.append(HumanReviewRecord.model_validate_json(path.read_text(encoding="utf-8")))
        return records


class HumanReviewService:
    """Create and decide backend human-review records."""

    def __init__(
        self,
        store: ReviewStore | None = None,
        guardrails: GuardrailService | None = None,
    ) -> None:
        self.store = store or ReviewStore()
        self.guardrails = guardrails or GuardrailService()

    def prepare_review(
        self, case_id: str, mode: ExecutionMode = ExecutionMode.MOCK_MCP
    ) -> HumanReviewRecord:
        """Run orchestration, validate guardrails and create a pending review."""
        result = run_agent_assessment(case_id, mode)
        guardrail_result = self.guardrails.check_draft(
            result.agent_draft,
            result.deterministic_assessment,
        )
        if not guardrail_result.safe_for_human_review:
            raise DomainValidationError("guardrails blocked draft preparation for human review")
        record = _record_from_agent_result(result, guardrail_result.findings)
        record = _refresh_record_hash(record)
        self.store.save(record)
        return record

    def decide(
        self,
        review_id: str,
        decision: HumanReviewDecision,
        reviewer_id: str,
        comments: str | None = None,
        reason: str | None = None,
        amendments: list[HumanReviewAmendment] | None = None,
    ) -> HumanReviewRecord:
        """Apply an explicit human review decision."""
        reviewer_id = _validate_reviewer_id(reviewer_id)
        record = self.store.load(review_id)
        integrity = self.verify_integrity(review_id, persist_invalid=False)
        if not integrity["valid"]:
            record = self._invalidate(record, "integrity verification failed before decision")
            self.store.save(record)
            raise DomainValidationError("review integrity verification failed")
        if record.status != HumanReviewStatus.PENDING:
            raise DomainValidationError(f"review is not pending: {record.status.value}")
        if decision == HumanReviewDecision.APPROVE:
            record = self._approve(record, reviewer_id, comments)
        elif decision == HumanReviewDecision.AMEND:
            if not reason:
                raise DomainValidationError("amend decision requires a reason")
            record = self._amend(record, reviewer_id, reason, amendments or [])
        elif decision == HumanReviewDecision.REJECT:
            if not reason:
                raise DomainValidationError("reject decision requires a reason")
            record = self._reject(record, reviewer_id, reason)
        else:
            raise DomainValidationError(f"unsupported review decision: {decision}")
        record = _refresh_record_hash(record)
        self.store.save(record)
        return record

    def verify_integrity(self, review_id: str, persist_invalid: bool = True) -> dict[str, object]:
        """Verify record, draft and deterministic assessment hashes."""
        record = self.store.load(review_id)
        findings = self.guardrails.check_review_state(record).findings
        expected_record_hash = _hash_record(record)
        if record.integrity.record_hash != expected_record_hash:
            findings.append(
                GuardrailFinding(
                    category=GuardrailCategory.DETERMINISTIC_OVERRIDE,
                    severity=GuardrailSeverity.BLOCKING,
                    message="review record hash mismatch",
                    field="integrity.record_hash",
                )
            )
        valid = not findings
        if not valid and persist_invalid and record.status != HumanReviewStatus.INVALIDATED:
            record = self._invalidate(record, "integrity verification failed")
            self.store.save(record)
        return {
            "review_id": review_id,
            "valid": valid,
            "findings": [finding.model_dump(mode="json") for finding in findings],
            "demonstration_only": True,
            "authenticated_identity": False,
            "submitted": False,
        }

    def _approve(
        self, record: HumanReviewRecord, reviewer_id: str, comments: str | None
    ) -> HumanReviewRecord:
        now = datetime.now(UTC)
        return _append_history(
            record.model_copy(
                update={
                    "reviewer_id": reviewer_id,
                    "decision": HumanReviewDecision.APPROVE,
                    "status": HumanReviewStatus.APPROVED_FOR_DEMONSTRATION,
                    "comments": comments,
                    "decided_at": now,
                }
            ),
            "approved for synthetic demonstration only",
            reviewer_id,
            comments,
        )

    def _amend(
        self,
        record: HumanReviewRecord,
        reviewer_id: str,
        reason: str,
        amendments: list[HumanReviewAmendment],
    ) -> HumanReviewRecord:
        if not amendments:
            raise DomainValidationError("amend decision requires at least one amendment")
        for amendment in amendments:
            validate_amendment_field(amendment.field)
        now = datetime.now(UTC)
        return _append_history(
            record.model_copy(
                update={
                    "reviewer_id": reviewer_id,
                    "decision": HumanReviewDecision.AMEND,
                    "status": HumanReviewStatus.AMENDMENT_REQUIRED,
                    "comments": reason,
                    "amendments": [*record.amendments, *amendments],
                    "decided_at": now,
                }
            ),
            "amendment required",
            reviewer_id,
            reason,
        )

    def _reject(
        self, record: HumanReviewRecord, reviewer_id: str, reason: str
    ) -> HumanReviewRecord:
        now = datetime.now(UTC)
        return _append_history(
            record.model_copy(
                update={
                    "reviewer_id": reviewer_id,
                    "decision": HumanReviewDecision.REJECT,
                    "status": HumanReviewStatus.REJECTED,
                    "comments": reason,
                    "decided_at": now,
                }
            ),
            "rejected",
            reviewer_id,
            reason,
        )

    def _invalidate(self, record: HumanReviewRecord, reason: str) -> HumanReviewRecord:
        return _append_history(
            record.model_copy(update={"status": HumanReviewStatus.INVALIDATED}),
            reason,
            None,
            reason,
        )


def _record_from_agent_result(
    result: AgentExecutionResult, findings: list[GuardrailFinding]
) -> HumanReviewRecord:
    now = datetime.now(UTC)
    draft = result.agent_draft.model_dump(mode="json")
    assessment = result.deterministic_assessment.model_dump(mode="json")
    draft_hash = sha256_hash(draft)
    assessment_hash = sha256_hash(assessment)
    review_id = f"REV-{uuid4()}"
    history = [
        ReviewHistoryEntry(
            sequence=1,
            status=HumanReviewStatus.PENDING,
            event="review prepared",
            created_at=now,
            findings=findings,
        )
    ]
    return HumanReviewRecord(
        review_id=review_id,
        request_id=result.request_id,
        case_id=result.case_id,
        audit_trace_id=result.audit_trace_id,
        draft_hash=draft_hash,
        deterministic_assessment_hash=assessment_hash,
        status=HumanReviewStatus.PENDING,
        created_at=now,
        history=history,
        integrity=ReviewIntegrityMetadata(
            draft_hash=draft_hash,
            deterministic_assessment_hash=assessment_hash,
        ),
        guardrail_findings=findings,
        draft=draft,
        deterministic_assessment=assessment,
        demonstration_only=True,
        authenticated_identity=False,
        submitted=False,
    )


def _append_history(
    record: HumanReviewRecord,
    event: str,
    reviewer_id: str | None,
    comments: str | None,
) -> HumanReviewRecord:
    entry = ReviewHistoryEntry(
        sequence=len(record.history) + 1,
        status=record.status,
        event=event,
        reviewer_id=reviewer_id,
        comments=comments,
        created_at=datetime.now(UTC),
    )
    return record.model_copy(update={"history": [*record.history, entry]})


def _refresh_record_hash(record: HumanReviewRecord) -> HumanReviewRecord:
    integrity = record.integrity.model_copy(update={"record_hash": _hash_record(record)})
    updated = record.model_copy(update={"integrity": integrity})
    if updated.history:
        history = [*updated.history]
        history[-1] = history[-1].model_copy(update={"record_hash": integrity.record_hash})
        updated = updated.model_copy(update={"history": history})
        integrity = updated.integrity.model_copy(update={"record_hash": _hash_record(updated)})
        updated = updated.model_copy(update={"integrity": integrity})
    return updated


def _hash_record(record: HumanReviewRecord) -> str:
    payload = record.model_dump(mode="json")
    payload["integrity"]["record_hash"] = None
    for entry in payload.get("history", []):
        entry["record_hash"] = None
    return sha256_hash(payload)


def _validate_reviewer_id(reviewer_id: str) -> str:
    value = validate_safe_identifier(reviewer_id, "reviewer_id")
    if "@" in value:
        raise DomainValidationError("reviewer_id must be an alias, not an email address")
    return value


def load_amendments_from_file(path: Path) -> list[HumanReviewAmendment]:
    """Load permitted amendments from a safe JSON file path."""
    if ".." in str(path) or path.is_absolute():
        raise DomainValidationError("amendment file must be a relative safe path")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        raise DomainValidationError("amendment file must contain an object or list")
    return [HumanReviewAmendment.model_validate(item) for item in payload]


def human_review_service() -> HumanReviewService:
    """Return a default human-review service."""
    return HumanReviewService()
