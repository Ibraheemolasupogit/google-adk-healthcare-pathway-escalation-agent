"""Deterministic tools for loading and validating synthetic cases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from schemas.assessment import BreachStatus
from schemas.case import PathwayCode, SyntheticPathwayCase

from tools.exceptions import CaseNotFoundError, DomainValidationError
from tools.pathway_tools import calculate_elapsed_time, determine_breach_status, get_pathway_rule

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES_PATH = PROJECT_ROOT / "data" / "synthetic_cases.json"

PROHIBITED_IDENTITY_FIELDS = {
    "patient_name",
    "name",
    "nhs_number",
    "hospital_number",
    "date_of_birth",
    "dob",
    "address",
    "postcode",
    "telephone",
    "phone",
    "email",
}


def load_synthetic_cases(path: Path = DEFAULT_CASES_PATH) -> list[SyntheticPathwayCase]:
    """Load and validate all synthetic cases from controlled local JSON."""
    with path.open(encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, list):
        raise DomainValidationError("synthetic case file must contain a list")

    cases = [validate_synthetic_case(raw_case) for raw_case in payload]
    _validate_unique_case_ids(cases)
    return cases


def get_case_by_id(
    case_id: str,
    cases: list[SyntheticPathwayCase] | None = None,
) -> SyntheticPathwayCase:
    """Return a synthetic case by ID."""
    loaded_cases = load_synthetic_cases() if cases is None else cases
    for case in loaded_cases:
        if case.case_id == case_id:
            return case
    raise CaseNotFoundError(f"No synthetic case found for {case_id}.")


def validate_synthetic_case(raw_case: dict[str, Any]) -> SyntheticPathwayCase:
    """Validate one synthetic case payload and reject unsafe or unsupported data."""
    prohibited = detect_prohibited_identity_fields(raw_case)
    if prohibited:
        raise DomainValidationError(
            f"case contains prohibited identity fields: {sorted(prohibited)}"
        )

    case = SyntheticPathwayCase.model_validate(raw_case)
    if case.assessment_datetime < case.referral_or_arrival_datetime:
        raise DomainValidationError("assessment datetime cannot be earlier than referral/arrival")

    rule = get_pathway_rule(case.pathway_code)
    calculate_elapsed_time(
        case.referral_or_arrival_datetime,
        case.assessment_datetime,
        rule.target_unit,
    )
    return case


def list_cases_by_pathway(pathway_code: PathwayCode) -> list[SyntheticPathwayCase]:
    """List synthetic cases for one pathway code."""
    return [case for case in load_synthetic_cases() if case.pathway_code == pathway_code]


def list_cases_by_breach_status(breach_status: BreachStatus) -> list[SyntheticPathwayCase]:
    """List synthetic cases that currently calculate to a breach status."""
    matches: list[SyntheticPathwayCase] = []
    for case in load_synthetic_cases():
        rule = get_pathway_rule(case.pathway_code)
        elapsed = calculate_elapsed_time(
            case.referral_or_arrival_datetime,
            case.assessment_datetime,
            rule.target_unit,
        )
        consumption = elapsed.value / rule.target_value * 100
        if determine_breach_status(round(consumption, 2), rule) == breach_status:
            matches.append(case)
    return matches


def detect_prohibited_identity_fields(raw_case: dict[str, Any]) -> set[str]:
    """Return prohibited identity field names present in a raw case payload."""
    return PROHIBITED_IDENTITY_FIELDS.intersection(raw_case)


def _validate_unique_case_ids(cases: list[SyntheticPathwayCase]) -> None:
    seen: set[str] = set()
    for case in cases:
        if case.case_id in seen:
            raise DomainValidationError(f"Duplicate case ID: {case.case_id}")
        seen.add(case.case_id)
