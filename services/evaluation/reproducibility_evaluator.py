"""Reproducibility evaluator."""

from __future__ import annotations

from datetime import UTC, datetime

from schemas.agent import AgentRequest, ExecutionMode
from schemas.evaluation import EvaluationFailure, ReproducibilityResult

from services.agent_config import load_agent_runtime_config
from services.agent_orchestrator import AgentOrchestrator
from services.assessment_service import assess_case
from services.evaluation.benchmark_loader import load_benchmark_cases
from services.evaluation.common import failure, metric, normalised_hash, suite_result


def evaluate_reproducibility() -> ReproducibilityResult:
    """Evaluate repeated deterministic, mock and mock-MCP reproducibility."""
    started = datetime.now(UTC)
    cases = load_benchmark_cases()
    selected = cases[:5]
    failures: list[EvaluationFailure] = []
    det_ok = mock_ok = mcp_ok = 0
    for case in cases:
        if normalised_hash(assess_case(case).model_dump(mode="json")) == normalised_hash(
            assess_case(case).model_dump(mode="json")
        ):
            det_ok += 1
        else:
            failures.append(
                failure(case.case_id, "deterministic_repro", True, False, "hash mismatch")
            )
    for case in selected:
        for mode in [ExecutionMode.MOCK, ExecutionMode.MOCK_MCP]:
            first = AgentOrchestrator(load_agent_runtime_config(mode)).run(
                AgentRequest(request_id=f"REPRO-A-{case.case_id}", case=case, execution_mode=mode)
            )
            second = AgentOrchestrator(load_agent_runtime_config(mode)).run(
                AgentRequest(request_id=f"REPRO-B-{case.case_id}", case=case, execution_mode=mode)
            )
            if normalised_hash(first.model_dump(mode="json")) == normalised_hash(
                second.model_dump(mode="json")
            ):
                if mode == ExecutionMode.MOCK:
                    mock_ok += 1
                else:
                    mcp_ok += 1
            else:
                failures.append(
                    failure(case.case_id, f"{mode.value}_repro", True, False, "hash mismatch")
                )
    metrics = [
        metric("deterministic_reproducibility_rate", det_ok / len(cases), 1.0),
        metric("mock_reproducibility_rate", mock_ok / len(selected), 1.0),
        metric("mock_mcp_reproducibility_rate", mcp_ok / len(selected), 1.0),
    ]
    return ReproducibilityResult.model_validate(
        suite_result(
            started_at=started,
            case_count=len(cases) + (len(selected) * 2),
            failures=failures,
            metrics=metrics,
            execution_mode="reproducibility",
            reproducibility_metadata={
                "normalised_fields": [
                    "request_id",
                    "audit_trace_id",
                    "trace_id",
                    "timestamps",
                    "duration_ms",
                    "review_id",
                    "record_hash",
                ]
            },
        ).model_dump()
    )
