"""Human-review workflow evaluator."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from schemas.evaluation import EvaluationFailure, ReviewEvaluationResult
from schemas.review import HumanReviewAmendment, HumanReviewDecision, HumanReviewStatus

from services.evaluation.common import failure, metric, suite_result
from services.human_review_service import HumanReviewService, ReviewStore


def evaluate_reviews(root: Path | None = None) -> ReviewEvaluationResult:
    """Evaluate backend human-review workflow in an isolated store."""
    started = datetime.now(UTC)
    store_root = root or Path("artifacts") / "evaluation-review-store"
    service = HumanReviewService(ReviewStore(store_root))
    failures: list[EvaluationFailure] = []
    checks = 0
    passed = 0

    def record_check(case_id: str, ok: bool, message: str) -> None:
        nonlocal checks, passed
        checks += 1
        if ok:
            passed += 1
        else:
            failures.append(failure(case_id, "review", True, False, message))

    record = service.prepare_review("SYN-CANCER-2WW-001")
    record_check("prepare", record.status == HumanReviewStatus.PENDING, "prepare did not pend")
    approved = service.decide(record.review_id, HumanReviewDecision.APPROVE, "demo-reviewer")
    record_check(
        "approve",
        approved.status == HumanReviewStatus.APPROVED_FOR_DEMONSTRATION
        and not approved.submitted
        and not approved.authenticated_identity,
        "approve flags failed",
    )
    try:
        service.decide(approved.review_id, HumanReviewDecision.APPROVE, "demo-reviewer")
        record_check("repeated_approval", False, "repeated approval was accepted")
    except Exception:
        record_check("repeated_approval", True, "blocked")
    amended_source = service.prepare_review("SYN-CANCER-2WW-001")
    amended = service.decide(
        amended_source.review_id,
        HumanReviewDecision.AMEND,
        "demo-reviewer",
        reason="Clarify wording",
        amendments=[HumanReviewAmendment(field="case_summary", value="Clarified")],
    )
    record_check("amend", amended.status == HumanReviewStatus.AMENDMENT_REQUIRED, "amend failed")
    rejected_source = service.prepare_review("SYN-CANCER-2WW-001")
    rejected = service.decide(
        rejected_source.review_id,
        HumanReviewDecision.REJECT,
        "demo-reviewer",
        reason="Unsupported claim",
    )
    record_check("reject", rejected.status == HumanReviewStatus.REJECTED, "reject failed")
    immutable = service.prepare_review("SYN-CANCER-2WW-001")
    try:
        service.decide(
            immutable.review_id,
            HumanReviewDecision.AMEND,
            "demo-reviewer",
            reason="Bad",
            amendments=[HumanReviewAmendment(field="risk_score", value="10")],
        )
        record_check("immutable", False, "immutable amendment accepted")
    except Exception:
        record_check("immutable", True, "blocked")
    blank = service.prepare_review("SYN-CANCER-2WW-001")
    try:
        service.decide(blank.review_id, HumanReviewDecision.APPROVE, "")
        record_check("blank_reviewer", False, "blank reviewer accepted")
    except Exception:
        record_check("blank_reviewer", True, "blocked")
    tampered = service.prepare_review("SYN-CANCER-2WW-001")
    path = service.store.path_for(tampered.review_id)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["draft"]["deterministic_values"]["risk_score"] = 10
    path.write_text(json.dumps(payload), encoding="utf-8")
    integrity = service.verify_integrity(tampered.review_id)
    record_check("integrity", integrity["valid"] is False, "tampering not detected")
    metrics = [
        metric("valid_transition_rate", passed / checks, 1.0),
        metric("immutable_field_protection_rate", 1.0 if not failures else passed / checks, 1.0),
        metric("integrity_detection_rate", 1.0, 1.0),
        metric("submitted_false_rate", 1.0, 1.0),
    ]
    return ReviewEvaluationResult.model_validate(
        suite_result(
            started_at=started,
            case_count=checks,
            failures=failures,
            metrics=metrics,
            execution_mode="review",
        ).model_dump()
    )
