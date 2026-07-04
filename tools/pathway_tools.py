"""Deterministic pathway rule and target calculation tools."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from schemas.assessment import BreachAssessment, BreachStatus, ElapsedTime, PathwayRule
from schemas.case import PathwayCode, TargetUnit

from tools.exceptions import DomainValidationError, PathwayRuleNotFoundError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES_PATH = PROJECT_ROOT / "data" / "pathway_targets.json"


def load_pathway_rules(path: Path = DEFAULT_RULES_PATH) -> tuple[str, list[PathwayRule]]:
    """Load and validate controlled demonstration pathway rules."""
    with path.open(encoding="utf-8") as file:
        payload = json.load(file)

    metadata = payload.get("metadata")
    rules_payload = payload.get("rules")
    if not isinstance(metadata, dict) or not isinstance(rules_payload, list):
        raise DomainValidationError("pathway target file must contain metadata and rules")

    rule_version = str(metadata.get("rule_version", "unknown"))
    rules = [PathwayRule.model_validate(rule) for rule in rules_payload]
    _validate_unique_pathway_codes(rules)
    return rule_version, rules


def get_pathway_rule(
    pathway_code: PathwayCode,
    rules: list[PathwayRule] | None = None,
) -> PathwayRule:
    """Return the pathway rule matching a supported pathway code."""
    _, loaded_rules = load_pathway_rules() if rules is None else ("provided", rules)
    for rule in loaded_rules:
        if rule.pathway_code == pathway_code:
            return rule
    raise PathwayRuleNotFoundError(f"No pathway rule found for {pathway_code}.")


def calculate_elapsed_time(
    start_datetime: datetime,
    end_datetime: datetime,
    target_unit: TargetUnit,
) -> ElapsedTime:
    """Calculate elapsed time from timezone-aware datetimes in the target unit."""
    if start_datetime.tzinfo is None or start_datetime.utcoffset() is None:
        raise DomainValidationError("start datetime must be timezone-aware")
    if end_datetime.tzinfo is None or end_datetime.utcoffset() is None:
        raise DomainValidationError("end datetime must be timezone-aware")
    if end_datetime < start_datetime:
        raise DomainValidationError("assessment datetime cannot be earlier than referral/arrival")

    elapsed_seconds = int((end_datetime - start_datetime).total_seconds())
    unit_seconds = _unit_seconds(target_unit)
    elapsed_value = _round_decimal(Decimal(elapsed_seconds) / Decimal(unit_seconds))
    return ElapsedTime(seconds=elapsed_seconds, value=float(elapsed_value), unit=target_unit)


def calculate_target_consumption(elapsed_time: ElapsedTime, rule: PathwayRule) -> float:
    """Return percentage of the target consumed, rounded to two decimals."""
    consumption = Decimal(str(elapsed_time.value)) / Decimal(rule.target_value) * Decimal(100)
    return float(_round_decimal(consumption))


def calculate_variance_from_target(elapsed_time: ElapsedTime, rule: PathwayRule) -> float:
    """Return elapsed time minus target value in the target unit."""
    variance = Decimal(str(elapsed_time.value)) - Decimal(rule.target_value)
    return float(_round_decimal(variance))


def determine_breach_status(target_consumption_percent: float, rule: PathwayRule) -> BreachStatus:
    """Classify target status using rule warning and critical thresholds.

    The deterministic logic is:
    - above critical threshold: substantially breached;
    - above 100 percent: breached;
    - exactly 100 percent: at target;
    - at or above warning threshold: approaching target;
    - otherwise: within target.
    """
    consumption = Decimal(str(target_consumption_percent))
    if consumption > Decimal(rule.critical_threshold_percent):
        return BreachStatus.SUBSTANTIALLY_BREACHED
    if consumption > Decimal(100):
        return BreachStatus.BREACHED
    if consumption == Decimal(100):
        return BreachStatus.AT_TARGET
    if consumption >= Decimal(rule.warning_threshold_percent):
        return BreachStatus.APPROACHING_TARGET
    return BreachStatus.WITHIN_TARGET


def assess_breach(elapsed_time: ElapsedTime, rule: PathwayRule) -> BreachAssessment:
    """Return elapsed, target consumption, variance, and breach status."""
    consumption = calculate_target_consumption(elapsed_time, rule)
    return BreachAssessment(
        elapsed_time=elapsed_time,
        target_consumption_percent=consumption,
        breach_status=determine_breach_status(consumption, rule),
        variance_from_target=calculate_variance_from_target(elapsed_time, rule),
    )


def _validate_unique_pathway_codes(rules: list[PathwayRule]) -> None:
    seen: set[PathwayCode] = set()
    for rule in rules:
        if rule.pathway_code in seen:
            raise DomainValidationError(f"Duplicate pathway code: {rule.pathway_code}")
        seen.add(rule.pathway_code)


def _unit_seconds(target_unit: TargetUnit) -> int:
    if target_unit == TargetUnit.HOURS:
        return 60 * 60
    if target_unit == TargetUnit.DAYS:
        return 24 * 60 * 60
    raise DomainValidationError(f"Unsupported target unit: {target_unit}")


def _round_decimal(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
