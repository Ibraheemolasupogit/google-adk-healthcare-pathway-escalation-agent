"""Pydantic models for synthetic pathway cases."""

from enum import StrEnum

from pydantic import BaseModel, Field


class PathwayType(StrEnum):
    """Supported demonstration pathway categories."""

    CANCER_2WW = "cancer_2ww"
    RTT = "rtt"
    UEC = "uec"


class SyntheticPathwayCase(BaseModel):
    """Minimal synthetic case record for future pathway assessment."""

    case_id: str = Field(pattern=r"^SYN-[A-Z0-9-]+$")
    synthetic: bool = True
    pathway_type: PathwayType
    referral_or_arrival_day: int = Field(ge=0)
    current_day: int = Field(ge=0)
    status: str
    operational_context: str
    human_review_required: bool = True
