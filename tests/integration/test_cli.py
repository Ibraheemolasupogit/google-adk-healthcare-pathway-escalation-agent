"""Integration tests for deterministic CLI workflows."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from schemas.assessment import PathwayAssessment

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the local CLI and capture output."""
    return subprocess.run(
        [sys.executable, "-m", "app.main", *args],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_cli_list_cases_works() -> None:
    result = run_cli("list-cases")

    assert result.returncode == 0
    assert "SYN-CANCER-2WW-001" in result.stdout


def test_cli_assess_case_works_with_json_schema_validation() -> None:
    result = run_cli("assess-case", "--case-id", "SYN-CANCER-2WW-001", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assessment = PathwayAssessment.model_validate(payload)
    assert assessment.case_id == "SYN-CANCER-2WW-001"


def test_cli_rejects_unknown_case_ids() -> None:
    result = run_cli("assess-case", "--case-id", "SYN-UNKNOWN-001")

    assert result.returncode == 2
    assert "ERROR:" in result.stdout


def test_cli_validate_data_works() -> None:
    result = run_cli("validate-data", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "valid"
    assert payload["synthetic_cases"] == 15


def test_cli_assess_all_works() -> None:
    result = run_cli("assess-all", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert len(payload) == 15


def test_cli_agent_assess_mock_works() -> None:
    result = run_cli("agent-assess", "--case-id", "SYN-CANCER-2WW-001", "--mode", "mock", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["execution_mode"] == "mock"
    assert payload["human_review_required"] is True
    assert payload["review_status"] == "PENDING"


def test_cli_agent_assess_rejects_unknown_case_id() -> None:
    result = run_cli("agent-assess", "--case-id", "SYN-UNKNOWN-001", "--mode", "mock")

    assert result.returncode == 2
    assert "ERROR:" in result.stdout


def test_cli_describe_agents_and_list_evidence_work() -> None:
    agents = run_cli("describe-agents", "--json")
    evidence = run_cli("list-evidence", "--json")

    assert agents.returncode == 0
    assert evidence.returncode == 0
    assert len(json.loads(agents.stdout)) == 6
    assert all(item["demonstration_only"] is True for item in json.loads(evidence.stdout))


def test_cli_validate_agent_config_works_without_credentials() -> None:
    result = run_cli("validate-agent-config", "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["google_adk_version"] == "1.36.0"
