"""Unit tests for deterministic pathway domain logic."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from pydantic import ValidationError
from schemas.assessment import BreachStatus, ReviewStatus, RiskLevel
from schemas.case import PathwayCode, Priority, SyntheticPathwayCase, TargetUnit
from services.assessment_service import assess_case, create_escalation_recommendation
from services.risk_engine import assign_risk_level
from tools.case_tools import (
    detect_prohibited_identity_fields,
    load_synthetic_cases,
    validate_synthetic_case,
)
from tools.exceptions import DomainValidationError
from tools.pathway_tools import (
    calculate_elapsed_time,
    calculate_target_consumption,
    determine_breach_status,
    get_pathway_rule,
    load_pathway_rules,
)


def test_pathway_rules_load_successfully() -> None:
    rule_version, rules = load_pathway_rules()

    assert rule_version == "2026-07-milestone-2-demo"
    assert len(rules) == 5


def test_pathway_codes_are_unique_and_targets_positive() -> None:
    _, rules = load_pathway_rules()

    codes = [rule.pathway_code for rule in rules]
    assert len(codes) == len(set(codes))
    assert all(rule.target_value > 0 for rule in rules)


def test_all_rules_are_demonstration_only() -> None:
    _, rules = load_pathway_rules()

    assert all(rule.demonstration_only is True for rule in rules)
    assert all(rule.validation_required is True for rule in rules)


def test_synthetic_cases_load_successfully_and_ids_are_unique() -> None:
    cases = load_synthetic_cases()

    assert len(cases) == 15
    assert len({case.case_id for case in cases}) == 15
    assert all(case.synthetic is True for case in cases)


def test_case_distribution_by_pathway() -> None:
    cases = load_synthetic_cases()
    counts = {code: 0 for code in PathwayCode}
    for case in cases:
        counts[case.pathway_code] += 1

    assert set(counts.values()) == {3}


def test_prohibited_identity_fields_are_rejected() -> None:
    raw_case = _valid_raw_case()
    raw_case["nhs_number"] = "9999999999"

    assert detect_prohibited_identity_fields(raw_case) == {"nhs_number"}
    with pytest.raises(DomainValidationError):
        validate_synthetic_case(raw_case)


def test_unsupported_pathway_codes_are_rejected() -> None:
    raw_case = _valid_raw_case()
    raw_case["pathway_code"] = "UNSUPPORTED"

    with pytest.raises(ValidationError):
        validate_synthetic_case(raw_case)


def test_invalid_timestamp_ordering_is_rejected() -> None:
    raw_case = _valid_raw_case()
    raw_case["assessment_datetime"] = "2026-06-30T09:00:00+00:00"

    with pytest.raises(DomainValidationError):
        validate_synthetic_case(raw_case)


def test_naive_datetimes_are_rejected() -> None:
    raw_case = _valid_raw_case()
    raw_case["assessment_datetime"] = "2026-07-02T09:00:00"

    with pytest.raises(ValidationError):
        validate_synthetic_case(raw_case)


def test_breach_status_classifications_cover_boundaries() -> None:
    rule = get_pathway_rule(PathwayCode.CANCER_2WW)

    assert determine_breach_status(50, rule) == BreachStatus.WITHIN_TARGET
    assert determine_breach_status(85, rule) == BreachStatus.APPROACHING_TARGET
    assert determine_breach_status(100, rule) == BreachStatus.AT_TARGET
    assert determine_breach_status(100.01, rule) == BreachStatus.BREACHED
    assert determine_breach_status(125.01, rule) == BreachStatus.SUBSTANTIALLY_BREACHED


def test_day_based_target_calculation() -> None:
    rule = get_pathway_rule(PathwayCode.CANCER_2WW)
    elapsed = calculate_elapsed_time(
        datetime(2026, 7, 1, 9, tzinfo=UTC),
        datetime(2026, 7, 8, 9, tzinfo=UTC),
        rule.target_unit,
    )

    assert elapsed.unit == TargetUnit.DAYS
    assert elapsed.value == 7.0
    assert calculate_target_consumption(elapsed, rule) == 50.0


def test_hour_based_target_calculation() -> None:
    rule = get_pathway_rule(PathwayCode.UEC_4_HOUR)
    elapsed = calculate_elapsed_time(
        datetime(2026, 7, 4, 10, tzinfo=UTC),
        datetime(2026, 7, 4, 13, 24, tzinfo=UTC),
        rule.target_unit,
    )

    assert elapsed.unit == TargetUnit.HOURS
    assert elapsed.value == 3.4
    assert calculate_target_consumption(elapsed, rule) == 85.0


def test_timezone_aware_calculation_across_offsets() -> None:
    elapsed = calculate_elapsed_time(
        datetime.fromisoformat("2026-07-04T10:00:00+01:00"),
        datetime.fromisoformat("2026-07-04T12:00:00+00:00"),
        TargetUnit.HOURS,
    )

    assert elapsed.value == 3.0


def test_risk_level_thresholds_are_correct() -> None:
    assert assign_risk_level(0) == RiskLevel.LOW
    assert assign_risk_level(2) == RiskLevel.LOW
    assert assign_risk_level(3) == RiskLevel.MODERATE
    assert assign_risk_level(4) == RiskLevel.MODERATE
    assert assign_risk_level(5) == RiskLevel.HIGH
    assert assign_risk_level(6) == RiskLevel.HIGH
    assert assign_risk_level(7) == RiskLevel.CRITICAL
    assert assign_risk_level(10) == RiskLevel.CRITICAL


def test_risk_scores_are_clamped_and_explained() -> None:
    case = _case("SYN-RTT-003")
    assessment = assess_case(case)

    assert 0 <= assessment.risk_score <= 10
    assert assessment.risk_factors
    assert all(factor.explanation for factor in assessment.risk_factors)
    assert all(factor.deterministic is True for factor in assessment.risk_factors)


def test_escalation_outputs_require_human_review_and_pending_status() -> None:
    recommendation = create_escalation_recommendation(_case("SYN-CANCER-2WW-003"))

    assert recommendation.human_review_required is True
    assert recommendation.review_status == ReviewStatus.PENDING
    assert recommendation.approved_by_human is False


def test_recommended_actions_are_non_clinical() -> None:
    assessment = assess_case(_case("SYN-CANCER-FDS-003"))
    prohibited_terms = {"diagnosis", "medication", "treatment advice", "clinical prioritisation"}

    assert assessment.recommended_actions
    for action in assessment.recommended_actions:
        assert action.non_clinical is True
        assert prohibited_terms.isdisjoint(action.description.lower().split())


def test_audit_trace_is_created() -> None:
    assessment = assess_case(_case("SYN-UEC-002"))

    assert assessment.audit_trace_id.startswith("TRACE-")
    assert assessment.audit_trace.trace_id == assessment.audit_trace_id
    assert assessment.audit_trace.calculation_steps
    assert assessment.audit_trace.human_review_required is True


def test_repeated_assessment_has_identical_calculations_except_trace_metadata() -> None:
    case = _case("SYN-CANCER-62-002")
    first = assess_case(case)
    second = assess_case(case)

    first_payload = first.model_dump(mode="json")
    second_payload = second.model_dump(mode="json")
    for payload in [first_payload, second_payload]:
        payload.pop("audit_trace_id")
        audit_trace = payload.pop("audit_trace")
        audit_trace.pop("trace_id")
        audit_trace.pop("started_at")
        audit_trace.pop("completed_at")
        payload["audit_trace"] = audit_trace

    assert first_payload == second_payload


def _case(case_id: str) -> SyntheticPathwayCase:
    return next(case for case in load_synthetic_cases() if case.case_id == case_id)


def _valid_raw_case() -> dict[str, Any]:
    base_time = datetime(2026, 7, 1, 9, tzinfo=UTC)
    return {
        "case_id": "SYN-CANCER-2WW-999",
        "synthetic": True,
        "pathway_code": "CANCER_2WW",
        "referral_or_arrival_datetime": base_time.isoformat(),
        "assessment_datetime": (base_time + timedelta(days=1)).isoformat(),
        "current_stage": "awaiting operational review",
        "priority": Priority.URGENT.value,
        "next_event_datetime": (base_time + timedelta(days=2)).isoformat(),
        "operational_flags": [],
        "source_system": "synthetic-test-system",
        "notes": "Synthetic test scenario.",
    }
