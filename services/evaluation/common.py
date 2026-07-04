"""Common helpers for deterministic evaluation services."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from schemas.evaluation import EvaluationFailure, EvaluationMetric, EvaluationSuiteResult

from services.evaluation.benchmark_loader import load_manifest
from services.security_utils import sha256_hash

EVALUATOR_VERSION = "1.0.0"
PASS_THRESHOLDS = {
    "deterministic_pathway_accuracy": 1.0,
    "breach_status_accuracy": 1.0,
    "deterministic_preservation_rate": 1.0,
    "human_review_enforcement_rate": 1.0,
    "immutable_field_protection_rate": 1.0,
    "submitted_false_rate": 1.0,
    "schema_compliance_rate": 1.0,
    "security_blocking_case_pass_rate": 1.0,
    "overall_controlled_benchmark_pass_rate": 0.95,
}


def failure(
    case_id: str,
    check: str,
    expected: Any,
    actual: Any,
    message: str,
) -> EvaluationFailure:
    """Create an evaluation failure."""
    return EvaluationFailure(
        case_id=case_id,
        check_name=check,
        expected=expected,
        actual=actual,
        message=message,
    )


def metric(name: str, value: float, threshold: float | None = None) -> EvaluationMetric:
    """Create a metric with pass/fail state."""
    return EvaluationMetric(
        name=name,
        value=round(value, 4),
        threshold=threshold,
        passed=True if threshold is None else value >= threshold,
    )


def suite_result(
    *,
    started_at: datetime,
    case_count: int,
    failures: list[EvaluationFailure],
    metrics: list[EvaluationMetric],
    execution_mode: str,
    checksums: dict[str, str] | None = None,
    warnings: list[str] | None = None,
    reproducibility_metadata: dict[str, Any] | None = None,
) -> EvaluationSuiteResult:
    """Build a common suite result."""
    manifest = load_manifest()
    failed_ids = {item.case_id for item in failures}
    passed_count = case_count - len(failed_ids)
    return EvaluationSuiteResult(
        evaluation_id=f"EVAL-{uuid4()}",
        evaluator_version=EVALUATOR_VERSION,
        benchmark_version=manifest.benchmark_version,
        started_at=started_at,
        completed_at=datetime.now(UTC),
        case_count=case_count,
        passed_count=passed_count,
        failed_count=len(failed_ids),
        skipped_count=0,
        pass_rate=round(passed_count / case_count, 4) if case_count else 0,
        metrics=metrics,
        failures=failures,
        warnings=warnings or [],
        execution_mode=execution_mode,
        demonstration_only=True,
        checksums=checksums or {},
        reproducibility_metadata=reproducibility_metadata or {},
    )


def normalise_volatile(payload: Any) -> Any:
    """Remove documented volatile fields before reproducibility hashing."""
    volatile_keys = {
        "request_id",
        "audit_trace_id",
        "trace_id",
        "started_at",
        "completed_at",
        "created_at",
        "decided_at",
        "duration_ms",
        "review_id",
        "record_hash",
    }
    if isinstance(payload, dict):
        return {
            key: normalise_volatile(value)
            for key, value in payload.items()
            if key not in volatile_keys
        }
    if isinstance(payload, list):
        return [normalise_volatile(item) for item in payload]
    if isinstance(payload, str):
        value = re.sub(r"TRACE-[0-9a-fA-F-]+", "TRACE-NORMALISED", payload)
        value = re.sub(r"REQ-[0-9a-fA-F-]+", "REQ-NORMALISED", value)
        value = re.sub(r"SKILL-[0-9a-fA-F-]+", "SKILL-NORMALISED", value)
        return value
    return payload


def normalised_hash(payload: Any) -> str:
    """Return a stable hash after documented volatile-field normalisation."""
    return sha256_hash(normalise_volatile(payload))
