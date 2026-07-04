"""Mock and mock-MCP agent evaluators."""

from __future__ import annotations

from datetime import UTC, datetime

from schemas.agent import AgentRequest, ExecutionMode
from schemas.evaluation import AgentEvaluationResult, EvaluationFailure, EvaluationSuiteResult

from services.agent_config import load_agent_runtime_config
from services.agent_orchestrator import AgentOrchestrator
from services.assessment_service import assess_case
from services.evaluation.benchmark_loader import load_benchmark_cases
from services.evaluation.common import failure, metric, suite_result
from services.guardrail_service import GuardrailService


def evaluate_agents(mode: ExecutionMode) -> AgentEvaluationResult:
    """Evaluate mock or mock-MCP orchestration."""
    started = datetime.now(UTC)
    cases = load_benchmark_cases()
    failures: list[EvaluationFailure] = []
    valid = preserved = grounded = claims_free = language_free = review_enforced = 0
    for case in cases:
        expected = assess_case(case)
        result = AgentOrchestrator(load_agent_runtime_config(mode)).run(
            AgentRequest(request_id=f"EVAL-{case.case_id}", case=case, execution_mode=mode)
        )
        valid += 1
        if (
            result.deterministic_assessment.model_copy(
                update={
                    "audit_trace_id": expected.audit_trace_id,
                    "audit_trace": expected.audit_trace,
                }
            )
            == expected
        ):
            preserved += 1
        else:
            failures.append(
                failure(case.case_id, "deterministic_preservation", True, False, "values changed")
            )
        if result.agent_draft.evidence:
            grounded += 1
        else:
            failures.append(failure(case.case_id, "evidence", True, False, "missing evidence"))
        if not result.agent_draft.unsupported_claims:
            claims_free += 1
        if (
            GuardrailService()
            .check_draft(result.agent_draft, result.deterministic_assessment)
            .passed
        ):
            language_free += 1
        else:
            failures.append(failure(case.case_id, "guardrails", True, False, "guardrails failed"))
        if result.human_review_required and result.review_status.value == "PENDING":
            review_enforced += 1
        else:
            failures.append(
                failure(case.case_id, "human_review", True, False, "human review not enforced")
            )
        if not result.agent_steps or not result.tool_invocations:
            failures.append(failure(case.case_id, "audit", True, False, "missing agent/tool trace"))
    total = len(cases)
    metrics = [
        metric("valid_output_rate", valid / total, 1.0),
        metric("deterministic_preservation_rate", preserved / total, 1.0),
        metric("evidence_grounding_rate", grounded / total, 1.0),
        metric("unsupported_claim_free_rate", claims_free / total, 1.0),
        metric("prohibited_language_free_rate", language_free / total, 1.0),
        metric("human_review_enforcement_rate", review_enforced / total, 1.0),
    ]
    return AgentEvaluationResult.model_validate(
        suite_result(
            started_at=started,
            case_count=total,
            failures=failures,
            metrics=metrics,
            execution_mode=mode.value,
        ).model_dump()
    )


def evaluate_execution_mode_parity() -> EvaluationSuiteResult:
    """Compare deterministic, mock and mock-MCP deterministic fields."""
    started = datetime.now(UTC)
    failures: list[EvaluationFailure] = []
    cases = load_benchmark_cases()
    for case in cases:
        direct = assess_case(case)
        values = {
            "pathway_code": direct.pathway_code.value,
            "target": direct.target.model_dump(mode="json"),
            "elapsed_time": direct.elapsed_time.model_dump(mode="json"),
            "breach_status": direct.breach_status.value,
            "risk_score": direct.risk_score,
            "risk_level": direct.risk_level.value,
            "actions": [action.action_code for action in direct.recommended_actions],
            "human_review_required": direct.human_review_required,
        }
        for mode in [ExecutionMode.MOCK, ExecutionMode.MOCK_MCP]:
            result = AgentOrchestrator(load_agent_runtime_config(mode)).run(
                AgentRequest(
                    request_id=f"PARITY-{case.case_id}-{mode.value}",
                    case=case,
                    execution_mode=mode,
                )
            )
            actual = {
                "pathway_code": result.deterministic_assessment.pathway_code.value,
                "target": result.deterministic_assessment.target.model_dump(mode="json"),
                "elapsed_time": result.deterministic_assessment.elapsed_time.model_dump(
                    mode="json"
                ),
                "breach_status": result.deterministic_assessment.breach_status.value,
                "risk_score": result.deterministic_assessment.risk_score,
                "risk_level": result.deterministic_assessment.risk_level.value,
                "actions": [
                    action.action_code
                    for action in result.deterministic_assessment.recommended_actions
                ],
                "human_review_required": result.human_review_required,
            }
            if actual != values:
                failures.append(
                    failure(
                        case.case_id,
                        f"parity_{mode.value}",
                        values,
                        actual,
                        "parity mismatch",
                    )
                )
    total = len(cases) * 2
    return suite_result(
        started_at=started,
        case_count=total,
        failures=failures,
        metrics=[metric("execution_mode_parity_rate", (total - len(failures)) / total, 1.0)],
        execution_mode="parity",
    )
