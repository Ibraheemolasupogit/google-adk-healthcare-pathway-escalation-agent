"""Integration tests for Milestone 7 deployment readiness."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_deployment_verifier_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/verify_deployment.py"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Milestone 7 deployment verification passed." in result.stdout


def test_dockerfile_uses_non_root_and_port() -> None:
    text = (PROJECT_ROOT / "deployment" / "Dockerfile").read_text(encoding="utf-8")

    assert "USER appuser" in text
    assert "PORT" in text
    assert "ui/streamlit_app.py" in text
    assert ".env" not in text


def test_dockerignore_excludes_runtime_and_credentials() -> None:
    text = (PROJECT_ROOT / "deployment" / ".dockerignore").read_text(encoding="utf-8")

    for item in [".env", ".git", "artifacts", "credentials", "service-account"]:
        assert item in text
