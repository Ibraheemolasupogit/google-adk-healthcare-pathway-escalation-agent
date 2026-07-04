"""Integration tests for placeholder command-line and validation workflows."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_placeholder_cli_runs_successfully() -> None:
    """The Milestone 1 CLI should run without external service calls."""
    result = subprocess.run(
        [sys.executable, "-m", "app.main"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "NHS Pathway Escalation and Evidence Agent" in result.stdout
    assert "Functional agent execution is not yet implemented." in result.stdout


def test_project_validation_script_succeeds() -> None:
    """The project validation script should pass on the Milestone 1 scaffold."""
    result = subprocess.run(
        [sys.executable, "scripts/validate_project.py"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Milestone 1 project validation passed." in result.stdout
