"""Schemas for backend human-review workflow."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, StrictBool, field_validator

from schemas.agent import ExecutionMode
from schemas.security import GuardrailFinding


class HumanReviewStatus(StrEnum):
    """Strict human-review states for synthetic demonstration outputs."""

    PENDING = "PENDING"
    APPROVED_FOR_DEMONSTRATION = "APPROVED_FOR_DEMONSTRATION"
    AMENDMENT_REQUIRED = "AMENDMENT_REQUIRED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    INVALIDATED = "INVALIDATED"


class HumanReviewDecision(StrEnum):
    """Explicit human-review decisions."""

    APPROVE = "APPROVE"
    AMEND = "AMEND"
    REJECT = "REJECT"


class HumanReviewAmendment(BaseModel):
    """Reviewer amendment to an allowed narrative field."""

    field: str
    value: str


class ReviewIntegrityMetadata(BaseModel):
    """Tamper-evident review integrity metadata."""

    algorithm: str = "sha256"
    draft_hash: str
    deterministic_assessment_hash: str
    record_hash: str | None = None


class ReviewHistoryEntry(BaseModel):
    """Append-only review history entry."""

    sequence: int = Field(ge=1)
    status: HumanReviewStatus
    event: str
    reviewer_id: str | None = None
    comments: str | None = None
    findings: list[GuardrailFinding] = Field(default_factory=list)
    created_at: datetime
    record_hash: str | None = None


class HumanReviewRequest(BaseModel):
    """Request to prepare a backend human-review record."""

    case_id: str
    execution_mode: ExecutionMode = ExecutionMode.MOCK_MCP


class HumanReviewRecord(BaseModel):
    """Stored backend human-review record."""

    review_id: str
    request_id: str
    case_id: str
    audit_trace_id: str
    draft_hash: str
    deterministic_assessment_hash: str
    reviewer_id: str | None = None
    decision: HumanReviewDecision | None = None
    status: HumanReviewStatus = HumanReviewStatus.PENDING
    comments: str | None = None
    amendments: list[HumanReviewAmendment] = Field(default_factory=list)
    created_at: datetime
    decided_at: datetime | None = None
    history: list[ReviewHistoryEntry] = Field(default_factory=list)
    integrity: ReviewIntegrityMetadata
    guardrail_findings: list[GuardrailFinding] = Field(default_factory=list)
    draft: dict[str, Any]
    deterministic_assessment: dict[str, Any]
    demonstration_only: StrictBool = True
    authenticated_identity: StrictBool = False
    submitted: StrictBool = False

    @field_validator("demonstration_only")
    @classmethod
    def require_demonstration_only(cls, value: bool) -> bool:
        """Review records are only synthetic demonstration metadata."""
        if value is not True:
            raise ValueError("review records must remain demonstration-only")
        return value

    @field_validator("authenticated_identity", "submitted")
    @classmethod
    def require_false_flags(cls, value: bool) -> bool:
        """Milestone 5 does not authenticate identity or submit outputs."""
        if value is not False:
            raise ValueError("review records cannot authenticate identity or submit outputs")
        return value
