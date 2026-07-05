"""Verify Milestone 7 UI and deployment readiness without external calls."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from schemas.agent import ExecutionMode  # noqa: E402
from tools.exceptions import DomainValidationError  # noqa: E402
from ui.config import SAFETY_BANNER, load_ui_config  # noqa: E402
from ui.health import run_health_checks  # noqa: E402

REQUIRED_FILES = [
    "ui/streamlit_app.py",
    "ui/demo_service.py",
    "ui/health.py",
    "deployment/Dockerfile",
    "deployment/.dockerignore",
    "deployment/README.md",
    "deployment/cloud-run.md",
    "deployment/service.yaml.example",
    "docs/evidence/milestone-6/evaluation-summary.md",
]
FORBIDDEN_PACKAGE_FILES = [".env", "service-account.json", "credentials.json"]


def main() -> int:
    """Run deployment verification."""
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (PROJECT_ROOT / relative).exists():
            errors.append(f"missing required file: {relative}")
    for relative in FORBIDDEN_PACKAGE_FILES:
        if (PROJECT_ROOT / relative).exists():
            errors.append(f"secret-like file must not be packaged: {relative}")
    try:
        importlib.import_module("ui.streamlit_app")
        config = load_ui_config()
        health = run_health_checks(config)
        if config.default_execution_mode != ExecutionMode.MOCK_MCP:
            errors.append("default UI execution mode must be mock-mcp")
        if config.enable_live_mode:
            errors.append("live mode must be disabled by default")
        if not health["mcp_default_works"]:
            errors.append("default mock-MCP execution failed")
        if not health["review_store_writable"]:
            errors.append("review store is not writable")
        if not SAFETY_BANNER:
            errors.append("safety banner text is missing")
        _verify_dockerfile(errors)
        _verify_dockerignore(errors)
    except (DomainValidationError, ImportError, OSError, ValueError) as exc:
        errors.append(f"deployment verification failed: {exc}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Milestone 7 deployment verification passed.")
    return 0


def _verify_dockerfile(errors: list[str]) -> None:
    text = (PROJECT_ROOT / "deployment" / "Dockerfile").read_text(encoding="utf-8")
    required = [
        "USER appuser",
        "STREAMLIT_SERVER_PORT",
        "PORT",
        "ui/streamlit_app.py",
        "HEALTHCHECK",
    ]
    for item in required:
        if item not in text:
            errors.append(f"Dockerfile missing required marker: {item}")
    if ".env" in text:
        errors.append("Dockerfile must not copy .env")


def _verify_dockerignore(errors: list[str]) -> None:
    text = (PROJECT_ROOT / "deployment" / ".dockerignore").read_text(encoding="utf-8")
    for item in [".env", ".git", "artifacts", "__pycache__", "credentials", "service-account"]:
        if item not in text:
            errors.append(f".dockerignore missing exclusion: {item}")


if __name__ == "__main__":
    raise SystemExit(main())
