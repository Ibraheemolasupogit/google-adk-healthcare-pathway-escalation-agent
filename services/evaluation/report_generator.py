"""Generate Milestone 6 evaluation reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from schemas.evaluation import EvaluationReport, EvaluationSuiteResult


def write_reports(report: EvaluationReport, output_dir: Path) -> None:
    """Write machine-readable and human-readable reports."""
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "evaluation-report.json", report.model_dump(mode="json"))
    _write_json(
        output_dir / "deterministic-results.json",
        report.deterministic.model_dump(mode="json"),
    )
    _write_json(
        output_dir / "agent-results.json",
        {
            "mock": report.agent_mock.model_dump(mode="json"),
            "mock_mcp": report.agent_mock_mcp.model_dump(mode="json"),
        },
    )
    _write_json(
        output_dir / "execution-mode-parity.json",
        report.execution_mode_parity.model_dump(mode="json"),
    )
    _write_json(output_dir / "skill-results.json", report.skills.model_dump(mode="json"))
    _write_json(output_dir / "evidence-results.json", report.evidence.model_dump(mode="json"))
    _write_json(output_dir / "security-results.json", report.security)
    _write_json(output_dir / "review-results.json", report.review.model_dump(mode="json"))
    _write_json(
        output_dir / "reproducibility-results.json",
        report.reproducibility.model_dump(mode="json"),
    )
    _write_json(output_dir / "failed-cases.json", report.failed_case_ids)
    _write_json(output_dir / "evaluation-manifest.json", report.manifest.model_dump(mode="json"))
    _write_markdown(output_dir / "evaluation-summary.md", report)
    _write_metric_csv(output_dir / "metric-summary.csv", report)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: Path, report: EvaluationReport) -> None:
    lines = [
        "# Milestone 6 Evaluation Summary",
        "",
        f"- Run ID: `{report.run_id}`",
        f"- Benchmark version: `{report.manifest.benchmark_version}`",
        f"- Evaluator version: `{report.manifest.evaluator_version}`",
        f"- Overall controlled benchmark pass rate: `{report.overall_pass_rate}`",
        "- Failed case IDs: "
        f"`{', '.join(report.failed_case_ids) if report.failed_case_ids else 'none'}`",
        "- Demonstration only: `true`",
        "",
        "## Suite Pass Rates",
    ]
    for name, suite in _suite_items(report):
        lines.append(f"- {name}: `{suite.pass_rate}` ({suite.passed_count}/{suite.case_count})")
    lines.extend(
        [
            "",
            "This evaluation uses synthetic data only and performs no live Gemini, "
            "NHS or network calls.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_metric_csv(path: Path, report: EvaluationReport) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["suite", "metric", "value", "threshold", "passed"])
        for suite_name, suite in _suite_items(report):
            for metric in suite.metrics:
                writer.writerow(
                    [
                        suite_name,
                        metric.name,
                        metric.value,
                        "" if metric.threshold is None else metric.threshold,
                        metric.passed,
                    ]
                )
        for key in ["precision", "recall", "f1", "blocking_case_pass_rate"]:
            writer.writerow(["security", key, report.security.get(key), "", ""])


def _suite_items(report: EvaluationReport) -> list[tuple[str, EvaluationSuiteResult]]:
    return [
        ("deterministic", report.deterministic),
        ("agent_mock", report.agent_mock),
        ("agent_mock_mcp", report.agent_mock_mcp),
        ("execution_mode_parity", report.execution_mode_parity),
        ("skills", report.skills),
        ("evidence", report.evidence),
        ("review", report.review),
        ("reproducibility", report.reproducibility),
    ]
