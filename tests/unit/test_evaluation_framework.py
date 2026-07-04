"""Tests for the Milestone 6 evaluation framework."""

from __future__ import annotations

import json
from pathlib import Path

from schemas.agent import AgentRequest, ExecutionMode
from services.agent_config import load_agent_runtime_config
from services.agent_orchestrator import AgentOrchestrator
from services.assessment_service import assess_case
from services.evaluation.agent_evaluator import (
    evaluate_agents,
    evaluate_execution_mode_parity,
)
from services.evaluation.benchmark_loader import (
    load_benchmark_cases,
    load_manifest,
    validate_benchmark,
)
from services.evaluation.common import normalise_volatile, normalised_hash
from services.evaluation.deterministic_evaluator import evaluate_deterministic
from services.evaluation.evidence_evaluator import evaluate_evidence
from services.evaluation.report_generator import write_reports
from services.evaluation.reproducibility_evaluator import evaluate_reproducibility
from services.evaluation.review_evaluator import evaluate_reviews
from services.evaluation.runner import run_full_evaluation
from services.evaluation.skill_evaluator import evaluate_skills


def test_benchmark_manifest_and_loader_are_valid() -> None:
    manifest = load_manifest()
    cases = load_benchmark_cases()
    validation = validate_benchmark()

    assert validation["status"] == "valid"
    assert manifest.case_count == 30
    assert len(cases) == 30
    assert {case.synthetic for case in cases} == {True}
    assert all(case.case_id.startswith("SYN-BENCH-") for case in cases)
    assert manifest.case_distribution == {
        "CANCER_2WW": 6,
        "CANCER_62": 6,
        "CANCER_FDS_28": 6,
        "RTT_18_WEEK": 6,
        "UEC_4_HOUR": 6,
    }


def test_deterministic_evaluator_passes_expected_outputs() -> None:
    result = evaluate_deterministic()

    assert result.case_count == 30
    assert result.failed_count == 0
    assert {metric.name: metric.value for metric in result.metrics}[
        "risk_score_exact_match_rate"
    ] == 1.0


def test_agent_evaluators_and_parity_pass() -> None:
    mock_result = evaluate_agents(ExecutionMode.MOCK)
    mcp_result = evaluate_agents(ExecutionMode.MOCK_MCP)
    parity = evaluate_execution_mode_parity()

    assert mock_result.failed_count == 0
    assert mcp_result.failed_count == 0
    assert parity.failed_count == 0
    assert parity.case_count == 60


def test_skill_evidence_review_and_reproducibility_evaluators_pass(tmp_path: Path) -> None:
    skills = evaluate_skills()
    evidence = evaluate_evidence()
    review = evaluate_reviews(tmp_path / "review-store")
    reproducibility = evaluate_reproducibility()

    assert skills.failed_count == 0
    assert evidence.failed_count == 0
    assert review.failed_count == 0
    assert reproducibility.failed_count == 0


def test_reproducibility_hash_normalises_documented_volatile_fields() -> None:
    left = {
        "request_id": "REQ-11111111-1111-1111-1111-111111111111",
        "created_at": "2026-07-04T12:00:00Z",
        "message": "Audit trace ID TRACE-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "stable": {"risk_score": 7.0},
    }
    right = {
        "request_id": "REQ-22222222-2222-2222-2222-222222222222",
        "created_at": "2026-07-04T12:01:00Z",
        "message": "Audit trace ID TRACE-bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "stable": {"risk_score": 7.0},
    }

    assert normalised_hash(left) == normalised_hash(right)


def test_mock_mcp_accepts_in_memory_benchmark_case() -> None:
    case = load_benchmark_cases()[0]
    result = AgentOrchestrator(load_agent_runtime_config(ExecutionMode.MOCK_MCP)).run(
        AgentRequest(
            request_id=f"TEST-{case.case_id}",
            case=case,
            execution_mode=ExecutionMode.MOCK_MCP,
        )
    )

    assert result.case_id == case.case_id
    assert normalise_volatile(
        result.deterministic_assessment.model_dump(mode="json")
    ) == normalise_volatile(assess_case(case).model_dump(mode="json"))
    assert result.execution_mode == ExecutionMode.MOCK_MCP


def test_full_evaluation_and_report_generation(tmp_path: Path) -> None:
    report, _ = run_full_evaluation(write_artifacts=False)
    output_dir = tmp_path / "evaluation-report"

    write_reports(report, output_dir)

    assert report.failed_case_ids == []
    assert report.overall_pass_rate == 1.0
    assert (output_dir / "evaluation-report.json").exists()
    assert (output_dir / "metric-summary.csv").exists()
    written = json.loads((output_dir / "evaluation-report.json").read_text(encoding="utf-8"))
    assert written["run_id"] == report.run_id
