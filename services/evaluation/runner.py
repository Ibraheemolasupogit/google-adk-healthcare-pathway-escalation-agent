"""Run the full deterministic Milestone 6 evaluation."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from schemas.agent import ExecutionMode
from schemas.evaluation import EvaluationReport
from schemas.security import SecurityEvaluationSummary

from services.evaluation.agent_evaluator import evaluate_agents, evaluate_execution_mode_parity
from services.evaluation.benchmark_loader import load_manifest
from services.evaluation.deterministic_evaluator import evaluate_deterministic
from services.evaluation.evidence_evaluator import evaluate_evidence
from services.evaluation.report_generator import write_reports
from services.evaluation.reproducibility_evaluator import evaluate_reproducibility
from services.evaluation.review_evaluator import evaluate_reviews
from services.evaluation.skill_evaluator import evaluate_skills
from services.security_evaluator import run_security_evaluation

ARTIFACT_ROOT = Path("artifacts") / "evaluation"


def run_full_evaluation(write_artifacts: bool = True) -> tuple[EvaluationReport, Path]:
    """Run all evaluation suites and optionally write reports."""
    run_id = f"EVAL-RUN-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
    manifest = load_manifest()
    deterministic = evaluate_deterministic()
    agent_mock = evaluate_agents(ExecutionMode.MOCK)
    agent_mock_mcp = evaluate_agents(ExecutionMode.MOCK_MCP)
    parity = evaluate_execution_mode_parity()
    skills = evaluate_skills()
    evidence = evaluate_evidence()
    security_summary = run_security_evaluation()
    review = evaluate_reviews(ARTIFACT_ROOT / run_id / "review-store")
    reproducibility = evaluate_reproducibility()
    failed_case_ids = sorted(
        {
            failure.case_id
            for suite in [
                deterministic,
                agent_mock,
                agent_mock_mcp,
                parity,
                skills,
                evidence,
                review,
                reproducibility,
            ]
            for failure in suite.failures
        }
        | {result.case_id for result in security_summary.results if not result.passed}
    )
    suites = [
        deterministic,
        agent_mock,
        agent_mock_mcp,
        parity,
        skills,
        evidence,
        review,
        reproducibility,
    ]
    suite_cases = sum(suite.case_count for suite in suites) + security_summary.total_cases
    suite_passed = sum(suite.passed_count for suite in suites) + security_summary.passed_cases
    report = EvaluationReport(
        run_id=run_id,
        manifest=manifest,
        deterministic=deterministic,
        agent_mock=agent_mock,
        agent_mock_mcp=agent_mock_mcp,
        execution_mode_parity=parity,
        skills=skills,
        evidence=evidence,
        security=_security_metrics(security_summary),
        review=review,
        reproducibility=reproducibility,
        overall_pass_rate=round(suite_passed / suite_cases, 4),
        failed_case_ids=failed_case_ids,
        demonstration_only=True,
    )
    output_dir = ARTIFACT_ROOT / run_id
    if write_artifacts:
        write_reports(report, output_dir)
    return report, output_dir


def _security_metrics(summary: SecurityEvaluationSummary) -> dict[str, object]:
    true_positives = sum(
        1 for result in summary.results if result.expected_blocking and result.actual_blocking
    )
    true_negatives = sum(
        1
        for result in summary.results
        if not result.expected_blocking and not result.actual_blocking
    )
    false_positives = summary.false_positives
    false_negatives = summary.false_negatives
    precision = true_positives / (true_positives + false_positives) if true_positives else 0
    recall = true_positives / (true_positives + false_negatives) if true_positives else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    blocking_cases = [result for result in summary.results if result.expected_blocking]
    blocking_passed = [result for result in blocking_cases if result.passed]
    category_results: dict[str, dict[str, int]] = {}
    for result in summary.results:
        for category in result.expected_categories:
            bucket = category_results.setdefault(category.value, {"expected": 0, "passed": 0})
            bucket["expected"] += 1
            if category in result.actual_categories:
                bucket["passed"] += 1
    return {
        "total_cases": summary.total_cases,
        "passed_cases": summary.passed_cases,
        "true_positives": true_positives,
        "true_negatives": true_negatives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "blocking_case_pass_rate": round(len(blocking_passed) / len(blocking_cases), 4),
        "category_results": category_results,
        "failed_case_ids": [result.case_id for result in summary.results if not result.passed],
        "controlled_dataset_note": "Scores describe this controlled synthetic dataset only.",
    }
