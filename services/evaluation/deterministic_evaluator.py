"""Deterministic assessment evaluator."""

from __future__ import annotations

from datetime import UTC, datetime

from schemas.evaluation import DeterministicEvaluationResult, EvaluationFailure

from services.assessment_service import assess_case
from services.evaluation.benchmark_loader import (
    load_benchmark_cases,
    load_expected_assessments,
    load_manifest,
)
from services.evaluation.common import failure, metric, suite_result


def evaluate_deterministic() -> DeterministicEvaluationResult:
    """Evaluate deterministic assessment exact-match behavior."""
    started = datetime.now(UTC)
    cases = load_benchmark_cases()
    expected = load_expected_assessments()
    failures: list[EvaluationFailure] = []
    checks = {
        "pathway": 0,
        "breach": 0,
        "risk_level": 0,
        "risk_score": 0,
        "actions": 0,
        "schema": 0,
    }
    for case in cases:
        actual = assess_case(case)
        exp = expected.get(case.case_id)
        if exp is None:
            failures.append(
                failure(
                    case.case_id,
                    "expected_exists",
                    True,
                    False,
                    "missing expected output",
                )
            )
            continue
        comparisons = [
            ("pathway", exp["pathway_code"], actual.pathway_code.value),
            (
                "elapsed_time",
                exp["expected_elapsed_time"],
                actual.elapsed_time.model_dump(mode="json"),
            ),
            (
                "target_consumption",
                exp["expected_target_consumption_percent"],
                actual.target_consumption_percent,
            ),
            ("variance", exp["expected_variance_from_target"], actual.variance_from_target),
            ("breach", exp["expected_breach_status"], actual.breach_status.value),
            ("risk_score", exp["expected_risk_score"], actual.risk_score),
            ("risk_level", exp["expected_risk_level"], actual.risk_level.value),
        ]
        for name, expected_value, actual_value in comparisons:
            if expected_value != actual_value:
                failures.append(
                    failure(
                        case.case_id,
                        name,
                        expected_value,
                        actual_value,
                        "deterministic mismatch",
                    )
                )
            elif name in checks:
                checks[name] += 1
        actual_factors = {factor.factor_code for factor in actual.risk_factors}
        if set(exp["required_risk_factor_codes"]).issubset(actual_factors):
            pass
        else:
            failures.append(
                failure(
                    case.case_id,
                    "risk_factors",
                    exp["required_risk_factor_codes"],
                    sorted(actual_factors),
                    "missing required risk factor",
                )
            )
        actual_actions = [action.action_code for action in actual.recommended_actions]
        if actual_actions == exp["expected_action_codes"]:
            checks["actions"] += 1
        else:
            failures.append(
                failure(
                    case.case_id,
                    "action_codes",
                    exp["expected_action_codes"],
                    actual_actions,
                    "action code mismatch",
                )
            )
        if actual.human_review_required and actual.demonstration_only and actual.audit_trace:
            checks["schema"] += 1
        else:
            failures.append(
                failure(case.case_id, "schema", True, False, "schema or review flags missing")
            )
    total = len(cases)
    metrics = [
        metric("pathway_accuracy", checks["pathway"] / total, 1.0),
        metric("breach_status_accuracy", checks["breach"] / total, 1.0),
        metric("risk_level_accuracy", checks["risk_level"] / total, 1.0),
        metric("risk_score_exact_match_rate", checks["risk_score"] / total, 1.0),
        metric("action_code_accuracy", checks["actions"] / total, 1.0),
        metric("schema_compliance_rate", checks["schema"] / total, 1.0),
    ]
    return DeterministicEvaluationResult.model_validate(
        suite_result(
            started_at=started,
            case_count=total,
            failures=failures,
            metrics=metrics,
            execution_mode="deterministic",
            checksums=load_manifest().expected_output_checksums,
        ).model_dump()
    )
