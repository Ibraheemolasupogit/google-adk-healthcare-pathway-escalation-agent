"""Unit tests for the backend human-review service."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from schemas.review import HumanReviewAmendment, HumanReviewDecision, HumanReviewStatus
from services.human_review_service import HumanReviewService, ReviewStore
from tools.exceptions import DomainValidationError


def review_service(tmp_path: Path) -> HumanReviewService:
    """Return a review service backed by a temporary store."""
    return HumanReviewService(ReviewStore(tmp_path / "reviews"))


def test_prepare_review_starts_pending_and_is_integrity_valid(tmp_path: Path) -> None:
    service = review_service(tmp_path)
    record = service.prepare_review("SYN-CANCER-2WW-001")

    assert record.status == HumanReviewStatus.PENDING
    assert record.demonstration_only is True
    assert record.authenticated_identity is False
    assert record.submitted is False
    assert record.reviewer_id is None
    assert service.verify_integrity(record.review_id)["valid"] is True


def test_approve_requires_reviewer_and_preserves_fixed_values(tmp_path: Path) -> None:
    service = review_service(tmp_path)
    record = service.prepare_review("SYN-CANCER-2WW-001")

    with pytest.raises(DomainValidationError):
        service.decide(record.review_id, HumanReviewDecision.APPROVE, "")

    approved = service.decide(
        record.review_id,
        HumanReviewDecision.APPROVE,
        "demo-reviewer",
        comments="Approved for synthetic demonstration",
    )

    assert approved.status == HumanReviewStatus.APPROVED_FOR_DEMONSTRATION
    assert approved.decision == HumanReviewDecision.APPROVE
    assert approved.submitted is False
    assert approved.authenticated_identity is False
    assert len(approved.history) == 2

    with pytest.raises(DomainValidationError):
        service.decide(approved.review_id, HumanReviewDecision.APPROVE, "demo-reviewer")


def test_amend_requires_reason_and_rejects_immutable_fields(tmp_path: Path) -> None:
    service = review_service(tmp_path)
    record = service.prepare_review("SYN-CANCER-2WW-001")

    with pytest.raises(DomainValidationError):
        service.decide(
            record.review_id,
            HumanReviewDecision.AMEND,
            "demo-reviewer",
            amendments=[HumanReviewAmendment(field="case_summary", value="Clarified wording")],
        )
    with pytest.raises(DomainValidationError):
        service.decide(
            record.review_id,
            HumanReviewDecision.AMEND,
            "demo-reviewer",
            reason="Do not alter deterministic values",
            amendments=[HumanReviewAmendment(field="risk_score", value="10")],
        )

    amended = service.decide(
        record.review_id,
        HumanReviewDecision.AMEND,
        "demo-reviewer",
        reason="Clarify wording",
        amendments=[HumanReviewAmendment(field="case_summary", value="Clarified wording")],
    )

    assert amended.status == HumanReviewStatus.AMENDMENT_REQUIRED
    assert amended.amendments[0].field == "case_summary"
    assert amended.submitted is False


def test_reject_requires_reason_and_records_provenance(tmp_path: Path) -> None:
    service = review_service(tmp_path)
    record = service.prepare_review("SYN-CANCER-2WW-001")

    with pytest.raises(DomainValidationError):
        service.decide(record.review_id, HumanReviewDecision.REJECT, "demo-reviewer")

    rejected = service.decide(
        record.review_id,
        HumanReviewDecision.REJECT,
        "demo-reviewer",
        reason="Unsupported operational claim",
    )

    assert rejected.status == HumanReviewStatus.REJECTED
    assert rejected.decision == HumanReviewDecision.REJECT
    assert rejected.comments == "Unsupported operational claim"
    assert rejected.history[-1].reviewer_id == "demo-reviewer"


def test_integrity_failure_invalidates_and_blocks_decision(tmp_path: Path) -> None:
    service = review_service(tmp_path)
    record = service.prepare_review("SYN-CANCER-2WW-001")
    path = service.store.path_for(record.review_id)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["draft"]["deterministic_values"]["risk_score"] = 10
    path.write_text(json.dumps(payload), encoding="utf-8")

    result = service.verify_integrity(record.review_id)

    assert result["valid"] is False
    invalidated = service.store.load(record.review_id)
    assert invalidated.status == HumanReviewStatus.INVALIDATED
    with pytest.raises(DomainValidationError):
        service.decide(record.review_id, HumanReviewDecision.APPROVE, "demo-reviewer")


def test_review_store_rejects_path_traversal_and_corruption(tmp_path: Path) -> None:
    store = ReviewStore(tmp_path / "reviews")

    with pytest.raises(DomainValidationError):
        store.path_for("../bad")

    service = HumanReviewService(store)
    record = service.prepare_review("SYN-CANCER-2WW-001")
    path = store.path_for(record.review_id)
    assert not path.with_suffix(".json.tmp").exists()
    path.write_text("{not-json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        store.load(record.review_id)
