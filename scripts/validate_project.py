"""Validate the Milestone 2 repository scaffold and deterministic data."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

REQUIRED_PATHS = [
    "README.md",
    "LICENSE",
    ".gitignore",
    ".env.example",
    "pyproject.toml",
    "Makefile",
    "app/main.py",
    "agents/coordinator.py",
    "tools/case_tools.py",
    "tools/pathway_tools.py",
    "services/risk_engine.py",
    "services/assessment_service.py",
    "data/synthetic_cases.json",
    "data/pathway_targets.json",
    "schemas/case.py",
    "schemas/assessment.py",
    "schemas/escalation.py",
    "docs/risk-scoring-methodology.md",
    "docs/deterministic-assessment-workflow.md",
    "docs/data-dictionary.md",
    "security/threat_model.md",
]


def validate_required_paths() -> list[str]:
    """Return missing required repository paths."""
    return [path for path in REQUIRED_PATHS if not (PROJECT_ROOT / path).exists()]


def validate_json_files() -> list[str]:
    """Return JSON parsing errors for controlled data files."""
    errors: list[str] = []
    for path in ["data/synthetic_cases.json", "data/pathway_targets.json"]:
        try:
            json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path} is invalid JSON: {exc}")
    return errors


def validate_domain_data() -> list[str]:
    """Return errors from deterministic domain data loaders."""
    from tools.case_tools import load_synthetic_cases
    from tools.pathway_tools import load_pathway_rules

    errors: list[str] = []
    try:
        _, rules = load_pathway_rules()
        if len(rules) != 5:
            errors.append("expected exactly five demonstration pathway rules")
    except Exception as exc:
        errors.append(f"pathway rules failed validation: {exc}")

    try:
        cases = load_synthetic_cases()
        if len(cases) < 15:
            errors.append("expected at least 15 synthetic cases")
    except Exception as exc:
        errors.append(f"synthetic cases failed validation: {exc}")
    return errors


def main() -> int:
    """Run project validation and return a shell status code."""
    errors = validate_required_paths()
    errors.extend(validate_json_files())
    errors.extend(validate_domain_data())

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Milestone 2 project validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
