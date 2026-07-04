"""Deterministic assessment orchestration for Milestone 2."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from schemas.assessment import (
    ActionPriority,
    AssessmentExecutionTrace,
    AuditEvent,
    BreachStatus,
    PathwayAssessment,
    PathwayRule,
    RecommendedAction,
    ReviewStatus,
    TargetSummary,
)
from schemas.case import SyntheticPathwayCase
from schemas.escalation import EscalationRecommendation
from tools.pathway_tools import assess_breach, calculate_elapsed_time, load_pathway_rules

from services.risk_engine import evaluate_operational_risk

DEMONSTRATION_WARNING = (
    "Demonstration-only output. Validate pathway targets against current authoritative NHS "
    "guidance before operational use."
)


def assess_case(case: SyntheticPathwayCase) -> PathwayAssessment:
    """Assess one synthetic pathway case deterministically."""
    started_at = datetime.now(UTC)
    rule_version, rules = load_pathway_rules()
    rule = _find_rule(case, rules)
    elapsed_time = calculate_elapsed_time(
        case.referral_or_arrival_datetime,
        case.assessment_datetime,
        rule.target_unit,
    )
    breach = assess_breach(elapsed_time, rule)
    risk = evaluate_operational_risk(case, breach, rule, rule.pathway_category)
    actions = generate_recommended_actions(case, breach.breach_status, risk.level.value)
    assumptions = generate_assumptions(rule)
    warnings = generate_warnings(case, rule, breach.breach_status)
    trace_id = f"TRACE-{uuid4()}"
    completed_at = datetime.now(UTC)
    audit_trace = AssessmentExecutionTrace(
        trace_id=trace_id,
        case_id=case.case_id,
        started_at=started_at,
        completed_at=completed_at,
        rule_version=rule_version,
        pathway_rule_used=rule.pathway_code,
        calculation_steps=[
            AuditEvent(
                sequence=1,
                event_type="RULE_LOADED",
                description="Loaded demonstration pathway rule.",
                data={"pathway_code": rule.pathway_code.value, "rule_version": rule_version},
            ),
            AuditEvent(
                sequence=2,
                event_type="ELAPSED_TIME_CALCULATED",
                description="Calculated elapsed time from referral or arrival to assessment.",
                data={"seconds": elapsed_time.seconds, "value": elapsed_time.value},
            ),
            AuditEvent(
                sequence=3,
                event_type="BREACH_STATUS_CLASSIFIED",
                description="Classified breach status from target consumption thresholds.",
                data={
                    "target_consumption_percent": breach.target_consumption_percent,
                    "breach_status": breach.breach_status.value,
                },
            ),
            AuditEvent(
                sequence=4,
                event_type="RISK_SCORE_CALCULATED",
                description="Calculated deterministic operational risk score.",
                data={"risk_score": risk.score, "risk_level": risk.level.value},
            ),
        ],
        risk_factors_applied=[factor.factor_code for factor in risk.factors],
        warnings=warnings,
        human_review_required=True,
        outcome_status=breach.breach_status,
    )

    return PathwayAssessment(
        case_id=case.case_id,
        pathway_code=rule.pathway_code,
        pathway_name=rule.pathway_name,
        pathway_category=rule.pathway_category,
        priority=case.priority,
        target=TargetSummary(
            value=rule.target_value,
            unit=rule.target_unit,
            description=rule.target_description,
            comparison_operator=rule.comparison_operator,
            warning_threshold_percent=rule.warning_threshold_percent,
            critical_threshold_percent=rule.critical_threshold_percent,
        ),
        elapsed_time=elapsed_time,
        target_consumption_percent=breach.target_consumption_percent,
        breach_status=breach.breach_status,
        variance_from_target=breach.variance_from_target,
        risk_score=risk.score,
        risk_level=risk.level,
        risk_factors=risk.factors,
        recommended_actions=actions,
        assumptions=assumptions,
        warnings=warnings,
        demonstration_only=True,
        human_review_required=True,
        review_status=ReviewStatus.PENDING,
        audit_trace_id=trace_id,
        audit_trace=audit_trace,
    )


def create_escalation_recommendation(case: SyntheticPathwayCase) -> EscalationRecommendation:
    """Create a structured non-clinical escalation draft from a deterministic assessment."""
    assessment = assess_case(case)
    return EscalationRecommendation(
        **assessment.model_dump(),
        escalation_summary=(
            f"{assessment.pathway_name} case {assessment.case_id} is "
            f"{assessment.breach_status.value} with {assessment.risk_level.value} operational risk."
        ),
        supporting_evidence=[
            "Local demonstration pathway target rule from data/pathway_targets.json."
        ],
        unsupported_claims=[],
        approved_by_human=False,
    )


def assess_cases(cases: list[SyntheticPathwayCase]) -> list[PathwayAssessment]:
    """Assess multiple synthetic cases deterministically."""
    return [assess_case(case) for case in cases]


def generate_recommended_actions(
    case: SyntheticPathwayCase,
    breach_status: BreachStatus,
    risk_level: str,
) -> list[RecommendedAction]:
    """Generate deterministic non-clinical operational actions."""
    actions = [
        RecommendedAction(
            action_code="VALIDATE_TARGET",
            description=(
                "Validate the applicable demonstration target against current authoritative "
                "guidance."
            ),
            priority=ActionPriority.HIGH,
        ),
        RecommendedAction(
            action_code="VERIFY_DATA_COMPLETENESS",
            description=(
                "Verify pathway data completeness and correct any operational data-quality issues."
            ),
            priority=ActionPriority.MEDIUM,
        ),
        RecommendedAction(
            action_code="CONFIRM_OWNER",
            description="Confirm the responsible operational pathway owner.",
            priority=ActionPriority.MEDIUM,
        ),
    ]
    if case.next_event_datetime is None:
        actions.append(
            RecommendedAction(
                action_code="REVIEW_NEXT_EVENT",
                description="Review and record the next scheduled operational event.",
                priority=ActionPriority.HIGH,
            )
        )
    if breach_status in {BreachStatus.BREACHED, BreachStatus.SUBSTANTIALLY_BREACHED}:
        actions.append(
            RecommendedAction(
                action_code="ESCALATE_COORDINATOR",
                description="Escalate to an authorised pathway coordinator for operational review.",
                priority=ActionPriority.CRITICAL
                if breach_status == BreachStatus.SUBSTANTIALLY_BREACHED
                else ActionPriority.HIGH,
            )
        )
    if risk_level in {"HIGH", "CRITICAL"}:
        actions.append(
            RecommendedAction(
                action_code="PRIORITISE_OPERATIONAL_REVIEW",
                description=(
                    "Prioritise non-clinical operational review of pathway status and next steps."
                ),
                priority=ActionPriority.HIGH,
            )
        )
    actions.append(
        RecommendedAction(
            action_code="RECORD_HUMAN_REVIEW",
            description="Record the outcome of human review before finalising any escalation.",
            priority=ActionPriority.HIGH,
        )
    )
    return actions


def generate_assumptions(rule: PathwayRule) -> list[str]:
    """Return deterministic assumptions made by the assessment service."""
    return [
        "Input case data is synthetic and supplied for demonstration only.",
        f"The {rule.pathway_code.value} target is loaded from local demonstration data.",
        "Elapsed time is rounded to two decimal places in the target unit.",
    ]


def generate_warnings(
    case: SyntheticPathwayCase,
    rule: PathwayRule,
    breach_status: BreachStatus,
) -> list[str]:
    """Return deterministic warnings for the assessment output."""
    warnings = [DEMONSTRATION_WARNING]
    if rule.validation_required:
        warnings.append("Pathway rule metadata requires validation before operational use.")
    if case.next_event_datetime is None:
        warnings.append("No next operational event is recorded for this synthetic case.")
    if breach_status in {BreachStatus.BREACHED, BreachStatus.SUBSTANTIALLY_BREACHED}:
        warnings.append("Breach status is operational and must be reviewed by an authorised human.")
    return warnings


def _find_rule(case: SyntheticPathwayCase, rules: list[PathwayRule]) -> PathwayRule:
    for rule in rules:
        if rule.pathway_code == case.pathway_code:
            return rule
    raise ValueError(f"No pathway rule found for {case.pathway_code}.")
