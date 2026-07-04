"""Validate the Milestone 1 repository scaffold."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "README.md",
    "LICENSE",
    ".gitignore",
    ".env.example",
    "pyproject.toml",
    "Makefile",
    "requirements.txt",
    "requirements-dev.txt",
    "app/main.py",
    "app/config.py",
    "agents/coordinator.py",
    "agents/pathway_agent.py",
    "agents/risk_agent.py",
    "agents/evidence_agent.py",
    "agents/escalation_agent.py",
    "agents/review_agent.py",
    "skills/identify_pathway/SKILL.md",
    "skills/calculate_risk/SKILL.md",
    "skills/retrieve_evidence/SKILL.md",
    "skills/generate_escalation/SKILL.md",
    "tools/case_tools.py",
    "tools/pathway_tools.py",
    "tools/evidence_tools.py",
    "mcp_servers/case_data_server.py",
    "mcp_servers/pathway_rules_server.py",
    "mcp_servers/policy_evidence_server.py",
    "data/synthetic_cases.json",
    "data/pathway_targets.json",
    "schemas/case.py",
    "schemas/assessment.py",
    "schemas/escalation.py",
    "evaluation/evaluator.py",
    "security/threat_model.md",
    "security/input_guardrails.py",
    "security/output_validation.py",
    "docs/architecture.md",
    "docs/system-specification.md",
    "docs/roadmap.md",
    "docs/evaluation-strategy.md",
    "docs/submission-plan.md",
    "docs/diagrams/architecture.mmd",
    "deployment/Dockerfile",
]

DISALLOWED_CASE_FIELDS = {
    "nhs_number",
    "hospital_number",
    "date_of_birth",
    "dob",
    "address",
    "postcode",
    "patient_name",
    "name",
}


def load_json(path: str) -> object:
    """Load a JSON file relative to the project root."""
    with (PROJECT_ROOT / path).open(encoding="utf-8") as file:
        return json.load(file)


def validate_required_paths() -> list[str]:
    """Return missing required repository paths."""
    return [path for path in REQUIRED_PATHS if not (PROJECT_ROOT / path).exists()]


def validate_synthetic_cases() -> list[str]:
    """Return validation errors for the synthetic sample dataset."""
    errors: list[str] = []
    data = load_json("data/synthetic_cases.json")
    if not isinstance(data, list):
        return ["data/synthetic_cases.json must contain a list of cases."]
    if len(data) != 3:
        errors.append("data/synthetic_cases.json must contain exactly three cases.")

    pathway_types = {case.get("pathway_type") for case in data if isinstance(case, dict)}
    expected_pathways = {"cancer_2ww", "rtt", "uec"}
    if pathway_types != expected_pathways:
        errors.append(f"synthetic cases must cover {sorted(expected_pathways)}.")

    for case in data:
        if not isinstance(case, dict):
            errors.append("each synthetic case must be a JSON object.")
            continue
        if case.get("synthetic") is not True:
            errors.append(f"{case.get('case_id', '<unknown>')} is not marked synthetic.")
        if case.get("human_review_required") is not True:
            errors.append(f"{case.get('case_id', '<unknown>')} must require human review.")
        forbidden = DISALLOWED_CASE_FIELDS.intersection(case)
        if forbidden:
            errors.append(f"{case.get('case_id', '<unknown>')} contains {sorted(forbidden)}.")
    return errors


def validate_targets() -> list[str]:
    """Return validation errors for demonstration target metadata."""
    data = load_json("data/pathway_targets.json")
    if not isinstance(data, dict):
        return ["data/pathway_targets.json must contain an object."]
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        return ["pathway target metadata is missing."]
    warning = str(metadata.get("warning", "")).lower()
    if "illustrative" not in warning or "authoritative" not in warning:
        return ["pathway target metadata must state values are illustrative and not authoritative."]
    return []


def main() -> int:
    """Run project validation and return a shell status code."""
    errors = validate_required_paths()
    errors.extend(validate_synthetic_cases())
    errors.extend(validate_targets())

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Milestone 1 project validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
