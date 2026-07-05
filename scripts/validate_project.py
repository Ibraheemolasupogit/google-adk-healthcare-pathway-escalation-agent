"""Validate the repository scaffold, data, UI, deployment and submission files."""

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
    "services/agent_orchestrator.py",
    "services/agent_config.py",
    "services/agent_review.py",
    "services/guardrail_service.py",
    "services/human_review_service.py",
    "services/security_evaluator.py",
    "services/security_utils.py",
    "services/skill_executor.py",
    "services/evaluation/benchmark_loader.py",
    "services/evaluation/deterministic_evaluator.py",
    "services/evaluation/agent_evaluator.py",
    "services/evaluation/skill_evaluator.py",
    "services/evaluation/evidence_evaluator.py",
    "services/evaluation/review_evaluator.py",
    "services/evaluation/reproducibility_evaluator.py",
    "services/evaluation/report_generator.py",
    "services/evaluation/runner.py",
    "ui/streamlit_app.py",
    "ui/components.py",
    "ui/demo_service.py",
    "ui/config.py",
    "ui/formatting.py",
    "ui/state.py",
    "ui/help_content.py",
    "ui/health.py",
    "scripts/verify_deployment.py",
    "scripts/final_submission_check.py",
    "deployment/Dockerfile",
    "deployment/.dockerignore",
    "deployment/README.md",
    "deployment/cloud-run.md",
    "deployment/service.yaml.example",
    "tools/adk_tools.py",
    "mcp_servers/common.py",
    "mcp_servers/registry.py",
    "mcp_servers/client.py",
    "data/synthetic_cases.json",
    "data/pathway_targets.json",
    "data/evidence/local_evidence.json",
    "schemas/case.py",
    "schemas/assessment.py",
    "schemas/escalation.py",
    "schemas/agent.py",
    "schemas/review.py",
    "schemas/security.py",
    "schemas/evaluation.py",
    "evaluation/benchmark_cases.json",
    "evaluation/expected_assessments.json",
    "evaluation/expected_agent_outputs.json",
    "evaluation/expected_skill_outputs.json",
    "evaluation/evidence_grounding_cases.json",
    "evaluation/review_cases.json",
    "evaluation/benchmark_manifest.json",
    "evaluation/security_cases.json",
    "docs/risk-scoring-methodology.md",
    "docs/deterministic-assessment-workflow.md",
    "docs/data-dictionary.md",
    "docs/adk-agent-architecture.md",
    "docs/agent-instructions.md",
    "docs/live-model-configuration.md",
    "docs/agent-execution-modes.md",
    "docs/mcp-architecture.md",
    "docs/mcp-tool-catalogue.md",
    "docs/agent-skills.md",
    "docs/mcp-security-model.md",
    "docs/mcp-local-development.md",
    "docs/tool-access-matrix.md",
    "docs/human-review-workflow.md",
    "docs/guardrail-architecture.md",
    "docs/review-state-machine.md",
    "docs/security-evaluation.md",
    "docs/data-and-secret-handling.md",
    "docs/deterministic-integrity.md",
    "docs/evaluation-framework.md",
    "docs/benchmark-dataset.md",
    "docs/evaluation-metrics.md",
    "docs/reproducibility-methodology.md",
    "docs/evaluation-limitations.md",
    "docs/user-interface.md",
    "docs/demo-walkthrough.md",
    "docs/deployment-architecture.md",
    "docs/cloud-run-readiness.md",
    "docs/ui-security.md",
    "docs/video-demo-plan.md",
    "docs/screenshot-plan.md",
    "submission/kaggle-writeup.md",
    "submission/title-options.md",
    "submission/elevator-pitch.md",
    "submission/course-concept-mapping.md",
    "submission/architecture-summary.md",
    "submission/video-script.md",
    "submission/video-recording-plan.md",
    "submission/video-shot-list.md",
    "submission/screenshot-plan.md",
    "submission/cover-image-brief.md",
    "submission/demo-commands.md",
    "submission/results-summary.md",
    "submission/responsible-ai.md",
    "submission/final-submission-checklist.md",
    "docs/evidence/milestone-6/evaluation-summary.md",
    "docs/evidence/milestone-6/metric-summary.csv",
    "docs/evidence/milestone-6/evaluation-manifest.json",
    "docs/evidence/milestone-6/benchmark-summary.json",
    "docs/evidence/milestone-6/limitations.md",
    "security/threat_model.md",
]


def validate_required_paths() -> list[str]:
    """Return missing required repository paths."""
    return [path for path in REQUIRED_PATHS if not (PROJECT_ROOT / path).exists()]


def validate_json_files() -> list[str]:
    """Return JSON parsing errors for controlled data files."""
    errors: list[str] = []
    for path in [
        "data/synthetic_cases.json",
        "data/pathway_targets.json",
        "evaluation/security_cases.json",
        "evaluation/benchmark_cases.json",
        "evaluation/expected_assessments.json",
        "evaluation/benchmark_manifest.json",
    ]:
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

    print("Milestone 8 project validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
