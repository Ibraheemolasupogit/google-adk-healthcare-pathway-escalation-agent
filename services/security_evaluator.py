"""Deterministic security evaluator for Milestone 5."""

from __future__ import annotations

import json
from pathlib import Path

from schemas.security import (
    GuardrailCategory,
    GuardrailResult,
    SecurityEvaluationCase,
    SecurityEvaluationResult,
    SecurityEvaluationSummary,
)
from tools.case_tools import get_case_by_id
from tools.exceptions import DomainValidationError

from services.guardrail_service import GuardrailService
from services.security_utils import validate_amendment_field

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SECURITY_CASES = PROJECT_ROOT / "evaluation" / "security_cases.json"


def load_security_cases(path: Path = DEFAULT_SECURITY_CASES) -> list[SecurityEvaluationCase]:
    """Load synthetic security evaluation cases."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [SecurityEvaluationCase.model_validate(item) for item in payload]


def run_security_evaluation(
    path: Path = DEFAULT_SECURITY_CASES,
) -> SecurityEvaluationSummary:
    """Run deterministic security evaluation without model calls."""
    guardrails = GuardrailService()
    results = [_evaluate_case(case, guardrails) for case in load_security_cases(path)]
    passed = sum(1 for result in results if result.passed)
    false_positives = sum(1 for result in results if result.false_positive)
    false_negatives = sum(1 for result in results if result.false_negative)
    return SecurityEvaluationSummary(
        total_cases=len(results),
        passed_cases=passed,
        pass_rate=round(passed / len(results), 4) if results else 0,
        false_positives=false_positives,
        false_negatives=false_negatives,
        results=results,
    )


def _evaluate_case(
    case: SecurityEvaluationCase, guardrails: GuardrailService
) -> SecurityEvaluationResult:
    result = _run_case(case, guardrails)
    actual_categories = sorted({finding.category for finding in result.findings})
    actual_blocking = not result.passed
    expected_categories = sorted(case.expected_categories)
    categories_ok = set(expected_categories).issubset(set(actual_categories))
    blocking_ok = actual_blocking == case.expected_blocking
    false_positive = actual_blocking and not case.expected_blocking
    false_negative = case.expected_blocking and not actual_blocking
    return SecurityEvaluationResult(
        case_id=case.case_id,
        passed=blocking_ok and categories_ok,
        expected_blocking=case.expected_blocking,
        actual_blocking=actual_blocking,
        expected_categories=expected_categories,
        actual_categories=actual_categories,
        false_positive=false_positive,
        false_negative=false_negative,
    )


def _run_case(case: SecurityEvaluationCase, guardrails: GuardrailService) -> GuardrailResult:
    if case.input_type == "text":
        text = str(case.payload.get("text", ""))
        if case.case_id == "SEC-016":
            text = text + ("X" * 6001)
        return guardrails.check_text(text)
    if case.input_type == "case":
        base = get_case_by_id("SYN-CANCER-2WW-001").model_dump(mode="json")
        base.update(case.payload)
        return guardrails.check_case_payload(base)
    if case.input_type == "evidence":
        return guardrails.check_evidence(case.payload)
    if case.input_type == "amendment":
        try:
            validate_amendment_field(str(case.payload.get("field", "")))
        except DomainValidationError as exc:
            from schemas.security import GuardrailFinding, GuardrailResult, GuardrailSeverity

            return GuardrailResult(
                passed=False,
                safe_for_human_review=False,
                findings=[
                    GuardrailFinding(
                        category=GuardrailCategory.INVALID_STATE_TRANSITION,
                        severity=GuardrailSeverity.BLOCKING,
                        message=str(exc),
                        field="field",
                    )
                ],
            )
    return guardrails.check_text(str(case.payload))
