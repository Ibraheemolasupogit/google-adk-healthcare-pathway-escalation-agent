"""Schemas for Milestone 5 security guardrails and evaluations."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, StrictBool


class GuardrailSeverity(StrEnum):
    """Guardrail finding severity."""

    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKING = "BLOCKING"


class GuardrailCategory(StrEnum):
    """Supported guardrail finding categories."""

    PROMPT_INJECTION = "PROMPT_INJECTION"
    DETERMINISTIC_OVERRIDE = "DETERMINISTIC_OVERRIDE"
    CLINICAL_ADVICE = "CLINICAL_ADVICE"
    AUTONOMOUS_ACTION = "AUTONOMOUS_ACTION"
    UNSUPPORTED_CLAIM = "UNSUPPORTED_CLAIM"
    SECRET_EXPOSURE = "SECRET_EXPOSURE"
    PERSONAL_DATA = "PERSONAL_DATA"
    MALFORMED_OUTPUT = "MALFORMED_OUTPUT"
    EVIDENCE_INJECTION = "EVIDENCE_INJECTION"
    TOOL_MISUSE = "TOOL_MISUSE"
    REVIEW_BYPASS = "REVIEW_BYPASS"
    OVERSIZED_INPUT = "OVERSIZED_INPUT"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    INVALID_STATE_TRANSITION = "INVALID_STATE_TRANSITION"


class GuardrailFinding(BaseModel):
    """One deterministic guardrail finding."""

    category: GuardrailCategory
    severity: GuardrailSeverity
    message: str
    field: str | None = None
    matched_text: str | None = None


class GuardrailResult(BaseModel):
    """Aggregate guardrail result."""

    passed: StrictBool
    safe_for_human_review: StrictBool
    findings: list[GuardrailFinding] = Field(default_factory=list)
    redacted_text: str | None = None


class SecurityEvaluationCase(BaseModel):
    """One synthetic deterministic security evaluation case."""

    case_id: str
    description: str
    input_type: str
    payload: dict[str, Any]
    expected_blocking: StrictBool
    expected_categories: list[GuardrailCategory]


class SecurityEvaluationResult(BaseModel):
    """Result for one synthetic security evaluation case."""

    case_id: str
    passed: StrictBool
    expected_blocking: StrictBool
    actual_blocking: StrictBool
    expected_categories: list[GuardrailCategory]
    actual_categories: list[GuardrailCategory]
    false_positive: StrictBool = False
    false_negative: StrictBool = False


class SecurityEvaluationSummary(BaseModel):
    """Aggregate security evaluation summary."""

    total_cases: int
    passed_cases: int
    pass_rate: float
    false_positives: int
    false_negatives: int
    results: list[SecurityEvaluationResult]
