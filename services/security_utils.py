"""Shared deterministic security utilities for Milestone 5."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from tools.exceptions import DomainValidationError

MAX_GUARDRAIL_TEXT_CHARS = 5000
MAX_EVIDENCE_SUMMARY_CHARS = 1200
SAFE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,120}$")
SECRET_PATTERNS = [
    re.compile(r"\b(?:api[_-]?key|secret|credential|password)\s*[:=]\s*['\"]?[^'\"\s]+", re.I),
    re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{12,}", re.I),
    re.compile(r"\b[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b"),
]
IMMUTABLE_REVIEW_FIELDS = {
    "case_id",
    "pathway_code",
    "pathway_name",
    "target",
    "elapsed_time",
    "breach_status",
    "variance_from_target",
    "risk_score",
    "risk_level",
    "risk_factors",
    "audit_trace_id",
    "demonstration_only",
    "human_review_required",
    "submitted",
}
AMENDABLE_REVIEW_FIELDS = {
    "case_summary",
    "operational_explanation",
    "evidence_summary",
    "recommended_action_wording",
    "reviewer_comments",
}


def canonical_json(payload: Any) -> str:
    """Return stable JSON for hashing and comparison."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def sha256_hash(payload: Any) -> str:
    """Return a SHA-256 hash over canonical JSON."""
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def redact_secrets(value: str) -> str:
    """Redact common deterministic secret patterns from text."""
    redacted = value
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("<redacted>", redacted)
    return redacted


def validate_safe_identifier(value: str, field_name: str) -> str:
    """Validate a safe identifier suitable for filenames or review metadata."""
    if not value or not SAFE_ID_PATTERN.fullmatch(value):
        raise DomainValidationError(f"{field_name} must be a safe non-blank identifier")
    if ".." in value or "/" in value or "\\" in value:
        raise DomainValidationError(f"{field_name} cannot contain path traversal")
    return value


def contains_path_traversal(value: str) -> bool:
    """Return whether text contains obvious path traversal markers."""
    return ".." in value or "/etc/" in value or "\\" in value


def extract_deterministic_values(assessment: dict[str, Any]) -> dict[str, Any]:
    """Extract deterministic fields that model output must not override."""
    return {
        "case_id": assessment.get("case_id"),
        "pathway_code": assessment.get("pathway_code"),
        "pathway_name": assessment.get("pathway_name"),
        "target": assessment.get("target"),
        "elapsed_time": assessment.get("elapsed_time"),
        "target_consumption_percent": assessment.get("target_consumption_percent"),
        "breach_status": assessment.get("breach_status"),
        "variance_from_target": assessment.get("variance_from_target"),
        "risk_score": assessment.get("risk_score"),
        "risk_level": assessment.get("risk_level"),
        "risk_factors": assessment.get("risk_factors"),
        "recommended_actions": assessment.get("recommended_actions"),
        "audit_trace_id": assessment.get("audit_trace_id"),
    }


def validate_amendment_field(field: str) -> None:
    """Validate that an amendment targets an explicitly allowed narrative field."""
    if field in IMMUTABLE_REVIEW_FIELDS or field not in AMENDABLE_REVIEW_FIELDS:
        raise DomainValidationError(f"amendment field is not permitted: {field}")
