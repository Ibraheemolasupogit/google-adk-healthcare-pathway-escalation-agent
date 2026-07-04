"""Pydantic models for synthetic pathway cases."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator


class PathwayCode(StrEnum):
    """Supported demonstration pathway codes."""

    CANCER_2WW = "CANCER_2WW"
    CANCER_FDS_28 = "CANCER_FDS_28"
    CANCER_62 = "CANCER_62"
    RTT_18_WEEK = "RTT_18_WEEK"
    UEC_4_HOUR = "UEC_4_HOUR"


class PathwayCategory(StrEnum):
    """Supported demonstration pathway categories."""

    CANCER = "CANCER"
    RTT = "RTT"
    UEC = "UEC"


class Priority(StrEnum):
    """Operational priority labels for synthetic cases."""

    STANDARD = "STANDARD"
    URGENT = "URGENT"
    HIGH = "HIGH"


class TargetUnit(StrEnum):
    """Target units supported by deterministic calculations."""

    HOURS = "HOURS"
    DAYS = "DAYS"


class ComparisonOperator(StrEnum):
    """Comparison operators supported by pathway rules."""

    LESS_THAN_OR_EQUAL = "LESS_THAN_OR_EQUAL"


class SyntheticPathwayCase(BaseModel):
    """Synthetic case record for deterministic pathway assessment."""

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(pattern=r"^SYN-[A-Z0-9-]+$")
    synthetic: StrictBool = True
    pathway_code: PathwayCode
    referral_or_arrival_datetime: datetime
    assessment_datetime: datetime
    current_stage: str = Field(min_length=1)
    priority: Priority
    next_event_datetime: datetime | None = None
    operational_flags: list[str] = Field(default_factory=list)
    source_system: str = Field(min_length=1)
    notes: str = Field(min_length=1)

    @field_validator(
        "referral_or_arrival_datetime",
        "assessment_datetime",
        "next_event_datetime",
    )
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        """Reject naive datetimes so elapsed-time calculations are reproducible."""
        if value is None:
            return value
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("datetime values must be timezone-aware")
        return value

    @field_validator("synthetic")
    @classmethod
    def require_synthetic(cls, value: bool) -> bool:
        """Ensure the case is explicitly marked synthetic."""
        if value is not True:
            raise ValueError("case must be marked synthetic")
        return value
