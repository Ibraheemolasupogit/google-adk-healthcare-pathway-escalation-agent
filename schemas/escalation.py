"""Pydantic models for escalation recommendation drafts."""

from pydantic import BaseModel, Field, StrictBool


class EscalationRecommendation(BaseModel):
    """Structured draft escalation requiring human review."""

    case_id: str
    summary: str
    recommended_actions: list[str] = Field(default_factory=list)
    supporting_evidence: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    human_review_required: StrictBool = True
    approved_by_human: StrictBool = False
