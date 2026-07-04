"""Deterministic operational risk scoring for synthetic pathway cases."""

from __future__ import annotations

from dataclasses import dataclass

from schemas.assessment import (
    BreachAssessment,
    BreachStatus,
    PathwayRule,
    RiskFactor,
    RiskLevel,
    SourceType,
)
from schemas.case import PathwayCategory, Priority, SyntheticPathwayCase, TargetUnit


@dataclass(frozen=True)
class RiskResult:
    """Aggregated deterministic operational risk result."""

    score: float
    level: RiskLevel
    factors: list[RiskFactor]


def evaluate_operational_risk(
    case: SyntheticPathwayCase,
    breach: BreachAssessment,
    rule: PathwayRule,
    pathway_category: PathwayCategory,
) -> RiskResult:
    """Evaluate deterministic, explainable operational risk from case and target status."""
    factors: list[RiskFactor] = []
    _add_breach_severity_factor(factors, breach.breach_status)
    _add_target_consumption_factor(factors, breach.target_consumption_percent)
    _add_priority_factor(factors, case.priority)
    _add_next_event_factors(factors, case, rule)
    _add_operational_flag_factor(factors, case)
    _add_substantial_breach_factor(factors, breach.breach_status)
    _add_time_sensitive_category_factor(factors, pathway_category)

    score = min(10.0, round(sum(factor.score_contribution for factor in factors), 2))
    return RiskResult(score=score, level=assign_risk_level(score), factors=factors)


def assign_risk_level(score: float) -> RiskLevel:
    """Assign risk level for a clamped score from 0 to 10."""
    clamped = min(10.0, max(0.0, score))
    if clamped <= 2:
        return RiskLevel.LOW
    if clamped <= 4:
        return RiskLevel.MODERATE
    if clamped <= 6:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def _risk_factor(
    factor_code: str,
    factor_name: str,
    score_contribution: float,
    explanation: str,
) -> RiskFactor:
    return RiskFactor(
        factor_code=factor_code,
        factor_name=factor_name,
        score_contribution=score_contribution,
        explanation=explanation,
        source_type=SourceType.DETERMINISTIC_RULE,
        deterministic=True,
    )


def _add_breach_severity_factor(factors: list[RiskFactor], status: BreachStatus) -> None:
    weights = {
        BreachStatus.WITHIN_TARGET: 0.0,
        BreachStatus.APPROACHING_TARGET: 1.0,
        BreachStatus.AT_TARGET: 1.5,
        BreachStatus.BREACHED: 2.5,
        BreachStatus.SUBSTANTIALLY_BREACHED: 4.0,
        BreachStatus.INVALID: 2.0,
    }
    factors.append(
        _risk_factor(
            "BREACH_SEVERITY",
            "Pathway breach severity",
            weights[status],
            f"Breach status is {status.value}.",
        )
    )


def _add_target_consumption_factor(
    factors: list[RiskFactor],
    target_consumption_percent: float,
) -> None:
    if target_consumption_percent < 75:
        contribution = 0.0
    elif target_consumption_percent < 100:
        contribution = 0.8
    elif target_consumption_percent <= 125:
        contribution = 1.2
    else:
        contribution = 2.0
    factors.append(
        _risk_factor(
            "TARGET_CONSUMPTION",
            "Percentage of target consumed",
            contribution,
            f"{target_consumption_percent:.2f}% of the demonstration target has elapsed.",
        )
    )


def _add_priority_factor(factors: list[RiskFactor], priority: Priority) -> None:
    weights = {Priority.STANDARD: 0.0, Priority.URGENT: 1.0, Priority.HIGH: 1.5}
    factors.append(
        _risk_factor(
            "PRIORITY",
            "Operational priority",
            weights[priority],
            f"Synthetic case priority is {priority.value}.",
        )
    )


def _add_next_event_factors(
    factors: list[RiskFactor],
    case: SyntheticPathwayCase,
    rule: PathwayRule,
) -> None:
    if case.next_event_datetime is None:
        factors.append(
            _risk_factor(
                "MISSING_NEXT_EVENT",
                "Missing next event",
                1.0,
                "No next operational event is recorded in the synthetic case.",
            )
        )
        return

    next_event_elapsed_seconds = (
        case.next_event_datetime - case.referral_or_arrival_datetime
    ).total_seconds()
    target_seconds = rule.target_value * (3600 if rule.target_unit == TargetUnit.HOURS else 86400)
    if next_event_elapsed_seconds > target_seconds:
        factors.append(
            _risk_factor(
                "NEXT_EVENT_AFTER_TARGET",
                "Next event after target",
                1.25,
                "The next operational event occurs after the demonstration target point.",
            )
        )


def _add_operational_flag_factor(
    factors: list[RiskFactor],
    case: SyntheticPathwayCase,
) -> None:
    contribution = min(1.2, 0.4 * len(case.operational_flags))
    factors.append(
        _risk_factor(
            "OPERATIONAL_FLAGS",
            "Existing operational flags",
            round(contribution, 2),
            f"{len(case.operational_flags)} operational flag(s) are present.",
        )
    )


def _add_substantial_breach_factor(factors: list[RiskFactor], status: BreachStatus) -> None:
    if status == BreachStatus.SUBSTANTIALLY_BREACHED:
        factors.append(
            _risk_factor(
                "SUBSTANTIAL_BREACH",
                "Substantial breach",
                1.0,
                "The case is beyond the configured critical threshold.",
            )
        )


def _add_time_sensitive_category_factor(
    factors: list[RiskFactor],
    category: PathwayCategory,
) -> None:
    contribution = 0.5 if category in {PathwayCategory.CANCER, PathwayCategory.UEC} else 0.0
    factors.append(
        _risk_factor(
            "TIME_SENSITIVE_CATEGORY",
            "Time-sensitive pathway category",
            contribution,
            f"Pathway category is {category.value}; this is an operational factor only.",
        )
    )
