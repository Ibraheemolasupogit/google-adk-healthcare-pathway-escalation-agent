"""Pydantic models for deterministic escalation recommendation drafts."""

from pydantic import ConfigDict, Field, StrictBool, field_validator

from schemas.assessment import PathwayAssessment, RecommendedAction, ReviewStatus, RiskFactor


class EscalationRecommendation(PathwayAssessment):
    """Structured non-clinical escalation draft requiring human review."""

    model_config = ConfigDict(extra="forbid")

    escalation_summary: str
    recommended_actions: list[RecommendedAction] = Field(default_factory=list)
    supporting_evidence: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    risk_factors: list[RiskFactor] = Field(default_factory=list)
    human_review_required: StrictBool = True
    review_status: ReviewStatus = ReviewStatus.PENDING
    approved_by_human: StrictBool = False

    @field_validator("approved_by_human")
    @classmethod
    def require_pending_approval(cls, value: bool) -> bool:
        """Milestone 2 drafts must not be pre-approved."""
        if value is not False:
            raise ValueError("deterministic draft escalations must not be pre-approved")
        return value
