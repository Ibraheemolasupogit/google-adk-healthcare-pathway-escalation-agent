"""Unit tests for importability, schemas, and synthetic data."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from schemas.escalation import EscalationRecommendation

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_core_modules_import_successfully() -> None:
    """Core placeholder modules should remain importable."""
    module_names = [
        "app.main",
        "agents.coordinator",
        "agents.pathway_agent",
        "agents.risk_agent",
        "agents.evidence_agent",
        "agents.escalation_agent",
        "agents.review_agent",
        "tools.case_tools",
        "tools.pathway_tools",
        "tools.evidence_tools",
        "mcp_servers.case_data_server",
        "mcp_servers.pathway_rules_server",
        "mcp_servers.policy_evidence_server",
        "security.input_guardrails",
        "security.output_validation",
        "evaluation.evaluator",
    ]

    for module_name in module_names:
        importlib.import_module(module_name)


def test_sample_data_files_contain_valid_json() -> None:
    """Synthetic data and target files should parse as JSON."""
    for path in [
        PROJECT_ROOT / "data" / "synthetic_cases.json",
        PROJECT_ROOT / "data" / "pathway_targets.json",
        PROJECT_ROOT / "evaluation" / "test_cases.json",
        PROJECT_ROOT / "evaluation" / "expected_outputs.json",
    ]:
        with path.open(encoding="utf-8") as file:
            json.load(file)


def test_three_sample_cases_are_synthetic() -> None:
    """The three required sample cases must be marked synthetic."""
    with (PROJECT_ROOT / "data" / "synthetic_cases.json").open(encoding="utf-8") as file:
        cases = json.load(file)

    assert len(cases) == 3
    assert {case["pathway_type"] for case in cases} == {"cancer_2ww", "rtt", "uec"}
    assert all(case["synthetic"] is True for case in cases)
    assert all(case["human_review_required"] is True for case in cases)


def test_sample_cases_do_not_contain_obvious_identifying_fields() -> None:
    """Sample cases should not include obvious patient-identifying fields."""
    disallowed = {
        "nhs_number",
        "hospital_number",
        "date_of_birth",
        "dob",
        "address",
        "postcode",
        "patient_name",
        "name",
    }
    with (PROJECT_ROOT / "data" / "synthetic_cases.json").open(encoding="utf-8") as file:
        cases = json.load(file)

    for case in cases:
        assert disallowed.isdisjoint(case)


def test_escalation_schema_requires_human_review_default() -> None:
    """Escalation recommendations should require human review by default."""
    draft = EscalationRecommendation(case_id="SYN-RTT-001", summary="Synthetic draft")

    assert draft.human_review_required is True
    assert draft.approved_by_human is False


def test_escalation_schema_rejects_invalid_human_review_type() -> None:
    """The schema should not silently accept invalid human-review values."""
    invalid_review_value: Any = "yes"
    try:
        EscalationRecommendation(
            case_id="SYN-RTT-001",
            summary="Synthetic draft",
            human_review_required=invalid_review_value,
        )
    except ValidationError:
        return
    raise AssertionError("Expected invalid human_review_required value to fail validation.")
