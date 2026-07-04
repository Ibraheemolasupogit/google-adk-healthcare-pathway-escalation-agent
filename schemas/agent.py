"""Pydantic schemas for Milestone 3 ADK agent orchestration."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

from schemas.assessment import PathwayAssessment, ReviewStatus
from schemas.case import PathwayCode, SyntheticPathwayCase


class ExecutionMode(StrEnum):
    """Supported orchestration execution modes."""

    DETERMINISTIC = "deterministic"
    MOCK = "mock"
    LIVE = "live"


class AgentName(StrEnum):
    """Milestone 3 specialist agent names."""

    COORDINATOR = "Coordinator Agent"
    PATHWAY = "Pathway Agent"
    RISK = "Risk Agent"
    EVIDENCE = "Evidence Agent"
    ESCALATION = "Escalation Agent"
    REVIEW = "Review Agent"


class ReviewSeverity(StrEnum):
    """Review finding severity."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class AgentRequest(BaseModel):
    """Input request for ADK orchestration."""

    request_id: str
    case_id: str | None = None
    case: SyntheticPathwayCase | None = None
    execution_mode: ExecutionMode = ExecutionMode.MOCK

    @field_validator("request_id")
    @classmethod
    def validate_request_id(cls, value: str) -> str:
        """Require a concise request identifier."""
        if not value or len(value) > 80:
            raise ValueError("request_id must be present and at most 80 characters")
        return value


class AgentStep(BaseModel):
    """Concise auditable agent step record."""

    sequence: int = Field(ge=1)
    agent_name: AgentName
    responsibility: str
    input_summary: str
    output_summary: str
    started_at: datetime
    completed_at: datetime


class AgentToolInvocation(BaseModel):
    """Concise auditable tool invocation record with safe summaries."""

    sequence: int = Field(ge=1)
    agent_name: AgentName
    tool_name: str
    input_summary: dict[str, Any]
    output_summary: dict[str, Any]
    started_at: datetime
    completed_at: datetime
    success: StrictBool


class LocalEvidenceDocument(BaseModel):
    """Controlled local demonstration evidence document."""

    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    title: str
    pathway_code: PathwayCode
    evidence_type: str
    summary: str
    source_label: str
    source_url_placeholder: str
    demonstration_only: StrictBool
    validation_required: StrictBool
    version: str

    @field_validator("demonstration_only", "validation_required")
    @classmethod
    def require_true_flags(cls, value: bool) -> bool:
        """Require demonstration and validation flags."""
        if value is not True:
            raise ValueError("local evidence must be demonstration-only and validation-required")
        return value


class AgentDraft(BaseModel):
    """Structured escalation draft produced by the orchestration layer."""

    case_id: str
    sections: dict[str, str]
    deterministic_values: dict[str, Any]
    evidence: list[LocalEvidenceDocument]
    unsupported_claims: list[str] = Field(default_factory=list)
    demonstration_only: StrictBool = True
    human_review_required: StrictBool = True
    review_status: ReviewStatus = ReviewStatus.PENDING

    @field_validator("human_review_required", "demonstration_only")
    @classmethod
    def require_true_flags(cls, value: bool) -> bool:
        """Final drafts must remain demonstration-only and review-gated."""
        if value is not True:
            raise ValueError("agent drafts must require human review and be demonstration-only")
        return value


class ReviewFinding(BaseModel):
    """Structured review finding."""

    finding_code: str
    severity: ReviewSeverity
    message: str
    field: str | None = None


class ReviewResult(BaseModel):
    """Structured review result for presenting a draft to a human reviewer."""

    safe_for_human_review: StrictBool
    findings: list[ReviewFinding]
    validation_passed: StrictBool
    prohibited_language_detected: StrictBool
    unsupported_claims_detected: StrictBool
    review_status: ReviewStatus = ReviewStatus.PENDING


class AgentExecutionResult(BaseModel):
    """Final validated result from the Milestone 3 agent orchestration layer."""

    request_id: str
    case_id: str
    deterministic_assessment: PathwayAssessment
    agent_draft: AgentDraft
    review_result: ReviewResult
    agent_steps: list[AgentStep]
    tool_invocations: list[AgentToolInvocation]
    warnings: list[str]
    demonstration_only: StrictBool = True
    human_review_required: StrictBool = True
    review_status: ReviewStatus = ReviewStatus.PENDING
    audit_trace_id: str
    model_metadata: dict[str, Any]
    execution_mode: ExecutionMode

    @field_validator("human_review_required", "demonstration_only")
    @classmethod
    def require_true_flags(cls, value: bool) -> bool:
        """Final results must always require human review."""
        if value is not True:
            raise ValueError("agent execution results must require human review")
        return value
