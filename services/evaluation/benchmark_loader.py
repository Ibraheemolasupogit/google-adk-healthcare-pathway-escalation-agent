"""Load and validate Milestone 6 benchmark datasets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from schemas.case import SyntheticPathwayCase
from schemas.evaluation import EvaluationManifest
from tools.exceptions import DomainValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_ROOT = PROJECT_ROOT / "evaluation"


def read_json(path: Path) -> Any:
    """Read JSON from a path."""
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    """Return SHA-256 checksum for a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest() -> EvaluationManifest:
    """Load the benchmark manifest."""
    return EvaluationManifest.model_validate(read_json(EVALUATION_ROOT / "benchmark_manifest.json"))


def load_benchmark_cases() -> list[SyntheticPathwayCase]:
    """Load synthetic benchmark cases."""
    cases: list[SyntheticPathwayCase] = []
    for item in read_json(EVALUATION_ROOT / "benchmark_cases.json"):
        payload = dict(item)
        payload.pop("benchmark_label", None)
        cases.append(SyntheticPathwayCase.model_validate(payload))
    return cases


def load_expected_assessments() -> dict[str, dict[str, Any]]:
    """Load expected deterministic assessment values keyed by case ID."""
    return {
        item["case_id"]: item for item in read_json(EVALUATION_ROOT / "expected_assessments.json")
    }


def load_expected_agent_outputs() -> dict[str, dict[str, Any]]:
    """Load expected agent outputs keyed by case ID."""
    return {
        item["case_id"]: item for item in read_json(EVALUATION_ROOT / "expected_agent_outputs.json")
    }


def load_expected_skill_outputs() -> dict[str, dict[str, Any]]:
    """Load expected skill outputs keyed by case ID."""
    return {
        item["case_id"]: item for item in read_json(EVALUATION_ROOT / "expected_skill_outputs.json")
    }


def load_evidence_grounding_cases() -> list[dict[str, Any]]:
    """Load evidence grounding cases."""
    return list(read_json(EVALUATION_ROOT / "evidence_grounding_cases.json"))


def load_review_cases() -> list[dict[str, Any]]:
    """Load human-review evaluation cases."""
    return list(read_json(EVALUATION_ROOT / "review_cases.json"))


def validate_benchmark() -> dict[str, Any]:
    """Validate benchmark manifest, checksums and distribution."""
    manifest = load_manifest()
    cases = load_benchmark_cases()
    errors: list[str] = []
    if manifest.case_count != len(cases):
        errors.append("manifest case_count does not match benchmark_cases.json")
    case_ids = [case.case_id for case in cases]
    if len(case_ids) != len(set(case_ids)):
        errors.append("benchmark case IDs must be unique")
    if not all(case.synthetic for case in cases):
        errors.append("all benchmark cases must be synthetic")
    for pathway, expected_count in manifest.case_distribution.items():
        actual = sum(1 for case in cases if case.pathway_code.value == pathway)
        if actual != expected_count:
            errors.append(f"pathway distribution mismatch for {pathway}: {actual}")
    for name, checksum in manifest.expected_output_checksums.items():
        filename = f"{name}.json"
        if name == "security_cases":
            filename = "security_cases.json"
        if file_sha256(EVALUATION_ROOT / filename) != checksum:
            errors.append(f"checksum mismatch for {filename}")
    if file_sha256(PROJECT_ROOT / "data" / "pathway_targets.json") != manifest.rule_data_checksum:
        errors.append("rule data checksum mismatch")
    if (
        file_sha256(PROJECT_ROOT / "data" / "evidence" / "local_evidence.json")
        != manifest.evidence_data_checksum
    ):
        errors.append("evidence data checksum mismatch")
    if errors:
        raise DomainValidationError("; ".join(errors))
    return {
        "status": "valid",
        "benchmark_version": manifest.benchmark_version,
        "case_count": len(cases),
        "case_distribution": manifest.case_distribution,
        "demonstration_only": manifest.demonstration_only,
    }
