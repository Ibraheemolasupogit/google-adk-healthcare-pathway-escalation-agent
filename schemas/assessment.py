"""Pydantic models for pathway assessment outputs."""

from pydantic import BaseModel, Field

from schemas.case import PathwayType


class PathwayAssessment(BaseModel):
    """Minimal structured assessment for a synthetic pathway case."""

    case_id: str
    pathway_type: PathwayType
    target_days: int = Field(gt=0)
    elapsed_days: int = Field(ge=0)
    breach_status: str
    risk_score: float = Field(ge=0, le=1)
    risk_factors: list[str] = Field(default_factory=list)
    evidence_references: list[str] = Field(default_factory=list)
    human_review_required: bool = True
