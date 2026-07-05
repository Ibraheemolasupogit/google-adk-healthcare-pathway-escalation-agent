"""Integration tests for final submission readiness checks."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_final_submission_check_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/final_submission_check.py"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Milestone 8 final submission check passed." in result.stdout
