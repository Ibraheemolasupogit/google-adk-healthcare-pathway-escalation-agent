"""Pydantic models for deterministic pathway assessment outputs."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

from schemas.case import (
    ComparisonOperator,
    PathwayCategory,
    PathwayCode,
    Priority,
    TargetUnit,
)


class BreachStatus(StrEnum):
    """Deterministic target status values."""

    WITHIN_TARGET = "WITHIN_TARGET"
    APPROACHING_TARGET = "APPROACHING_TARGET"
    AT_TARGET = "AT_TARGET"
    BREACHED = "BREACHED"
    SUBSTANTIALLY_BREACHED = "SUBSTANTIALLY_BREACHED"
    INVALID = "INVALID"


class RiskLevel(StrEnum):
    """Operational risk levels for the 0 to 10 risk score."""

    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ActionPriority(StrEnum):
    """Priority labels for deterministic operational actions."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReviewStatus(StrEnum):
    """Human-review lifecycle status."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"


class SourceType(StrEnum):
    """Source categories used in deterministic outputs."""

    DEMONSTRATION_CONFIG = "DEMONSTRATION_CONFIG"
    CASE_DATA = "CASE_DATA"
    DETERMINISTIC_RULE = "DETERMINISTIC_RULE"


class PathwayRule(BaseModel):
    """Controlled demonstration pathway target rule."""

    model_config = ConfigDict(extra="forbid")

    pathway_code: PathwayCode
    pathway_name: str
    pathway_category: PathwayCategory
    target_value: int = Field(gt=0)
    target_unit: TargetUnit
    target_description: str
    comparison_operator: ComparisonOperator
    warning_threshold_percent: int = Field(gt=0)
    critical_threshold_percent: int = Field(gt=0)
    source_title: str
    source_type: SourceType
    source_url_placeholder: str
    effective_date_placeholder: str
    demonstration_only: StrictBool
    validation_required: StrictBool
    notes: str

    @field_validator("demonstration_only", "validation_required")
    @classmethod
    def require_true_flags(cls, value: bool) -> bool:
        """Require demonstration and validation flags to be true."""
        if value is not True:
            raise ValueError("pathway rules must be demonstration-only and validation-required")
        return value


class TargetSummary(BaseModel):
    """Target details copied into final assessment outputs."""

    value: int = Field(gt=0)
    unit: TargetUnit
    description: str
    comparison_operator: ComparisonOperator
    warning_threshold_percent: int
    critical_threshold_percent: int


class ElapsedTime(BaseModel):
    """Elapsed waiting time represented in seconds and target units."""

    seconds: int = Field(ge=0)
    value: float = Field(ge=0)
    unit: TargetUnit
    rounded_to: str = "2 decimal places"


class BreachAssessment(BaseModel):
    """Deterministic breach assessment for a case and pathway rule."""

    elapsed_time: ElapsedTime
    target_consumption_percent: float = Field(ge=0)
    breach_status: BreachStatus
    variance_from_target: float


class RiskFactor(BaseModel):
    """Explainable contribution to the operational risk score."""

    factor_code: str
    factor_name: str
    score_contribution: float = Field(ge=0)
    explanation: str
    source_type: SourceType
    deterministic: StrictBool = True


class RecommendedAction(BaseModel):
    """Deterministic operational action recommendation."""

    action_code: str
    description: str
    priority: ActionPriority
    non_clinical: StrictBool = True


class AuditEvent(BaseModel):
    """A deterministic step recorded in an assessment execution trace."""

    sequence: int = Field(ge=1)
    event_type: str
    description: str
    data: dict[str, Any] = Field(default_factory=dict)


class AssessmentExecutionTrace(BaseModel):
    """Auditable deterministic execution record."""

    trace_id: str
    case_id: str
    started_at: datetime
    completed_at: datetime
    rule_version: str
    pathway_rule_used: PathwayCode
    calculation_steps: list[AuditEvent]
    risk_factors_applied: list[str]
    warnings: list[str]
    human_review_required: StrictBool = True
    outcome_status: BreachStatus


class PathwayAssessment(BaseModel):
    """Final deterministic pathway assessment output."""

    case_id: str
    pathway_code: PathwayCode
    pathway_name: str
    pathway_category: PathwayCategory
    priority: Priority
    target: TargetSummary
    elapsed_time: ElapsedTime
    target_consumption_percent: float = Field(ge=0)
    breach_status: BreachStatus
    variance_from_target: float
    risk_score: float = Field(ge=0, le=10)
    risk_level: RiskLevel
    risk_factors: list[RiskFactor]
    recommended_actions: list[RecommendedAction]
    assumptions: list[str]
    warnings: list[str]
    demonstration_only: StrictBool = True
    human_review_required: StrictBool = True
    review_status: ReviewStatus = ReviewStatus.PENDING
    audit_trace_id: str
    audit_trace: AssessmentExecutionTrace

    @field_validator("demonstration_only", "human_review_required")
    @classmethod
    def require_true_output_flags(cls, value: bool) -> bool:
        """Ensure final outputs remain demonstration-only and human-reviewed."""
        if value is not True:
            raise ValueError("final outputs must be demonstration-only and require human review")
        return value
