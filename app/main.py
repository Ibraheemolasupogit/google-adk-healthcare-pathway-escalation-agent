"""Deterministic and ADK agent command-line interface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from agents.registry import describe_agents
from mcp_servers.client import BoundedMCPClient
from mcp_servers.registry import get_server_definition, list_server_definitions
from schemas.agent import ExecutionMode
from schemas.review import HumanReviewDecision
from services.agent_orchestrator import (
    run_agent_assessment,
    validate_agent_configuration,
)
from services.assessment_service import assess_case, assess_cases
from services.evaluation.agent_evaluator import evaluate_agents
from services.evaluation.benchmark_loader import (
    load_benchmark_cases,
    read_json,
    validate_benchmark,
)
from services.evaluation.deterministic_evaluator import evaluate_deterministic
from services.evaluation.evidence_evaluator import evaluate_evidence
from services.evaluation.reproducibility_evaluator import evaluate_reproducibility
from services.evaluation.review_evaluator import evaluate_reviews
from services.evaluation.runner import ARTIFACT_ROOT, run_full_evaluation
from services.evaluation.skill_evaluator import evaluate_skills
from services.guardrail_service import GuardrailService
from services.human_review_service import (
    HumanReviewService,
    ReviewStore,
    load_amendments_from_file,
)
from services.risk_engine import assign_risk_level
from services.security_evaluator import run_security_evaluation
from services.skill_executor import execute_skill, list_skill_definitions
from tools.case_tools import get_case_by_id, load_synthetic_cases
from tools.evidence_tools import load_local_evidence
from tools.exceptions import CaseNotFoundError, DomainValidationError, PathwayRuleNotFoundError
from tools.pathway_tools import load_pathway_rules
from ui.config import SAFETY_BANNER, available_public_modes, load_ui_config
from ui.services import list_case_options, load_evaluation_evidence

ARTIFACT_DIR = Path("artifacts") / "assessments"


def build_parser() -> argparse.ArgumentParser:
    """Build the deterministic CLI parser."""
    parser = argparse.ArgumentParser(
        prog="python -m app.main",
        description="NHS Pathway Escalation and Evidence Agent deterministic CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_cases = subparsers.add_parser("list-cases", help="List synthetic case IDs.")
    list_cases.add_argument("--json", action="store_true", help="Output JSON.")

    show_case = subparsers.add_parser("show-case", help="Show one synthetic case.")
    show_case.add_argument("--case-id", required=True)
    show_case.add_argument("--json", action="store_true", help="Output JSON.")

    assess_case_parser = subparsers.add_parser("assess-case", help="Assess one synthetic case.")
    assess_case_parser.add_argument("--case-id", required=True)
    assess_case_parser.add_argument("--json", action="store_true", help="Output JSON.")
    assess_case_parser.add_argument("--write-artifact", action="store_true")

    assess_all = subparsers.add_parser("assess-all", help="Assess all synthetic cases.")
    assess_all.add_argument("--json", action="store_true", help="Output JSON.")
    assess_all.add_argument("--write-artifacts", action="store_true")

    list_pathways = subparsers.add_parser("list-pathways", help="List demonstration pathways.")
    list_pathways.add_argument("--json", action="store_true", help="Output JSON.")

    validate_data = subparsers.add_parser(
        "validate-data",
        help="Validate local case and rule data.",
    )
    validate_data.add_argument("--json", action="store_true", help="Output JSON.")

    describe_risk = subparsers.add_parser("describe-risk-model", help="Describe risk scoring.")
    describe_risk.add_argument("--json", action="store_true", help="Output JSON.")

    agent_assess = subparsers.add_parser("agent-assess", help="Run ADK agent orchestration.")
    agent_assess.add_argument("--case-id", required=True)
    agent_assess.add_argument(
        "--mode",
        choices=[mode.value for mode in ExecutionMode],
        default=ExecutionMode.MOCK.value,
    )
    agent_assess.add_argument("--json", action="store_true", help="Output JSON.")

    describe_agent_parser = subparsers.add_parser("describe-agents", help="Describe ADK agents.")
    describe_agent_parser.add_argument("--json", action="store_true", help="Output JSON.")

    validate_agent = subparsers.add_parser(
        "validate-agent-config",
        help="Validate non-secret agent configuration.",
    )
    validate_agent.add_argument(
        "--mode",
        choices=[mode.value for mode in ExecutionMode],
        default=ExecutionMode.MOCK.value,
    )
    validate_agent.add_argument("--json", action="store_true", help="Output JSON.")

    list_evidence = subparsers.add_parser("list-evidence", help="List local evidence.")
    list_evidence.add_argument("--json", action="store_true", help="Output JSON.")

    list_mcp = subparsers.add_parser("list-mcp-servers", help="List approved MCP servers.")
    list_mcp.add_argument("--json", action="store_true", help="Output JSON.")

    describe_mcp = subparsers.add_parser("describe-mcp-server", help="Describe one MCP server.")
    describe_mcp.add_argument("--server", required=True)
    describe_mcp.add_argument("--json", action="store_true", help="Output JSON.")

    validate_mcp = subparsers.add_parser("validate-mcp-config", help="Validate MCP registry.")
    validate_mcp.add_argument("--json", action="store_true", help="Output JSON.")

    mcp_get_case = subparsers.add_parser("mcp-get-case", help="Fetch a case through MCP.")
    mcp_get_case.add_argument("--case-id", required=True)
    mcp_get_case.add_argument("--json", action="store_true", help="Output JSON.")

    mcp_assess = subparsers.add_parser("mcp-assess-case", help="Assess a case through MCP.")
    mcp_assess.add_argument("--case-id", required=True)
    mcp_assess.add_argument("--json", action="store_true", help="Output JSON.")

    mcp_evidence = subparsers.add_parser("mcp-search-evidence", help="Search evidence through MCP.")
    mcp_evidence.add_argument("--pathway-code", required=True)
    mcp_evidence.add_argument("--query", default="")
    mcp_evidence.add_argument("--json", action="store_true", help="Output JSON.")

    list_skills = subparsers.add_parser("list-skills", help="List approved Agent Skills.")
    list_skills.add_argument("--json", action="store_true", help="Output JSON.")

    describe_skill = subparsers.add_parser("describe-skill", help="Describe one approved skill.")
    describe_skill.add_argument("--skill", required=True)
    describe_skill.add_argument("--json", action="store_true", help="Output JSON.")

    run_skill = subparsers.add_parser("run-skill", help="Run an approved local skill.")
    run_skill.add_argument("--skill", required=True)
    run_skill.add_argument("--case-id", required=True)
    run_skill.add_argument("--json", action="store_true", help="Output JSON.")

    guardrail_input = subparsers.add_parser(
        "guardrail-check-input", help="Run guardrails against free text."
    )
    guardrail_input.add_argument("--text", required=True)
    guardrail_input.add_argument("--json", action="store_true", help="Output JSON.")

    guardrail_case = subparsers.add_parser(
        "guardrail-check-case", help="Run guardrails against a synthetic case."
    )
    guardrail_case.add_argument("--case-id", required=True)
    guardrail_case.add_argument("--json", action="store_true", help="Output JSON.")

    guardrail_evidence = subparsers.add_parser(
        "guardrail-check-evidence", help="Run guardrails against local evidence."
    )
    guardrail_evidence.add_argument("--evidence-id", required=True)
    guardrail_evidence.add_argument("--json", action="store_true", help="Output JSON.")

    prepare_review = subparsers.add_parser("prepare-review", help="Prepare a human review.")
    prepare_review.add_argument("--case-id", required=True)
    prepare_review.add_argument(
        "--mode",
        choices=[mode.value for mode in ExecutionMode],
        default=ExecutionMode.MOCK_MCP.value,
    )
    prepare_review.add_argument("--json", action="store_true", help="Output JSON.")

    list_reviews = subparsers.add_parser("list-reviews", help="List local review records.")
    list_reviews.add_argument("--json", action="store_true", help="Output JSON.")

    show_review = subparsers.add_parser("show-review", help="Show one review record.")
    show_review.add_argument("--review-id", required=True)
    show_review.add_argument("--json", action="store_true", help="Output JSON.")

    decide_review = subparsers.add_parser("decide-review", help="Apply a human review decision.")
    decide_review.add_argument("--review-id", required=True)
    decide_review.add_argument("--decision", choices=["approve", "amend", "reject"], required=True)
    decide_review.add_argument("--reviewer-id", required=True)
    decide_review.add_argument("--comments")
    decide_review.add_argument("--reason")
    decide_review.add_argument("--amendment-file")
    decide_review.add_argument("--json", action="store_true", help="Output JSON.")

    verify_review = subparsers.add_parser("verify-review-integrity", help="Verify a review record.")
    verify_review.add_argument("--review-id", required=True)
    verify_review.add_argument("--json", action="store_true", help="Output JSON.")

    security_eval = subparsers.add_parser(
        "run-security-evaluation", help="Run deterministic security evaluation."
    )
    security_eval.add_argument("--json", action="store_true", help="Output JSON.")

    list_benchmark = subparsers.add_parser("list-benchmark-cases", help="List benchmark cases.")
    list_benchmark.add_argument("--json", action="store_true", help="Output JSON.")

    show_benchmark = subparsers.add_parser("show-benchmark-case", help="Show benchmark case.")
    show_benchmark.add_argument("--case-id", required=True)
    show_benchmark.add_argument("--json", action="store_true", help="Output JSON.")

    validate_benchmark_parser = subparsers.add_parser(
        "validate-benchmark", help="Validate benchmark datasets."
    )
    validate_benchmark_parser.add_argument("--json", action="store_true", help="Output JSON.")

    eval_det = subparsers.add_parser(
        "evaluate-deterministic",
        help="Evaluate deterministic engine.",
    )
    eval_det.add_argument("--json", action="store_true", help="Output JSON.")

    eval_agents = subparsers.add_parser("evaluate-agents", help="Evaluate mock agents.")
    eval_agents.add_argument("--mode", choices=["mock", "mock-mcp"], required=True)
    eval_agents.add_argument("--json", action="store_true", help="Output JSON.")

    eval_skills = subparsers.add_parser("evaluate-skills", help="Evaluate Agent Skills.")
    eval_skills.add_argument("--json", action="store_true", help="Output JSON.")

    eval_evidence = subparsers.add_parser("evaluate-evidence", help="Evaluate evidence grounding.")
    eval_evidence.add_argument("--json", action="store_true", help="Output JSON.")

    eval_reviews = subparsers.add_parser("evaluate-reviews", help="Evaluate human review.")
    eval_reviews.add_argument("--json", action="store_true", help="Output JSON.")

    eval_repro = subparsers.add_parser("evaluate-reproducibility", help="Evaluate reproducibility.")
    eval_repro.add_argument("--json", action="store_true", help="Output JSON.")

    full_eval = subparsers.add_parser("run-full-evaluation", help="Run full evaluation.")
    full_eval.add_argument("--json", action="store_true", help="Output JSON.")

    show_eval = subparsers.add_parser(
        "show-evaluation-summary", help="Show generated evaluation summary."
    )
    show_eval.add_argument("--run-id", required=True)
    show_eval.add_argument("--json", action="store_true", help="Output JSON.")

    ui_info = subparsers.add_parser("ui-info", help="Show safe UI configuration.")
    ui_info.add_argument("--json", action="store_true", help="Output JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process status code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _run_command(args)
    except (CaseNotFoundError, DomainValidationError, PathwayRuleNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2


def _run_command(args: argparse.Namespace) -> int:
    if args.command == "list-cases":
        cases = load_synthetic_cases()
        case_rows: list[dict[str, str]] = [
            {
                "case_id": case.case_id,
                "pathway_code": case.pathway_code.value,
                "priority": case.priority.value,
            }
            for case in cases
        ]
        _emit(case_rows, args.json)
        return 0

    if args.command == "show-case":
        case = get_case_by_id(args.case_id)
        _emit(case.model_dump(mode="json"), args.json)
        return 0

    if args.command == "assess-case":
        case = get_case_by_id(args.case_id)
        assessment = assess_case(case)
        if args.write_artifact:
            _write_artifact(assessment.case_id, assessment.model_dump_json(indent=2))
        _emit(assessment.model_dump(mode="json"), args.json)
        return 0

    if args.command == "assess-all":
        assessments = assess_cases(load_synthetic_cases())
        if args.write_artifacts:
            for assessment in assessments:
                _write_artifact(assessment.case_id, assessment.model_dump_json(indent=2))
        _emit([assessment.model_dump(mode="json") for assessment in assessments], args.json)
        return 0

    if args.command == "list-pathways":
        rule_version, rules = load_pathway_rules()
        pathway_payload: dict[str, Any] = {
            "rule_version": rule_version,
            "rules": [rule.model_dump(mode="json") for rule in rules],
        }
        _emit(pathway_payload, args.json)
        return 0

    if args.command == "validate-data":
        rule_version, rules = load_pathway_rules()
        cases = load_synthetic_cases()
        validation_payload: dict[str, Any] = {
            "status": "valid",
            "rule_version": rule_version,
            "pathway_rules": len(rules),
            "synthetic_cases": len(cases),
            "warning": "Demonstration targets must be validated before operational use.",
        }
        _emit(validation_payload, args.json)
        return 0

    if args.command == "describe-risk-model":
        _emit(_risk_model_description(), args.json)
        return 0

    if args.command == "agent-assess":
        result = run_agent_assessment(args.case_id, ExecutionMode(args.mode))
        _emit(result.model_dump(mode="json"), args.json)
        return 0

    if args.command == "describe-agents":
        _emit(describe_agents(), args.json)
        return 0

    if args.command == "validate-agent-config":
        _emit(validate_agent_configuration(ExecutionMode(args.mode)), args.json)
        return 0

    if args.command == "list-evidence":
        _emit([item.model_dump(mode="json") for item in load_local_evidence()], args.json)
        return 0

    if args.command == "list-mcp-servers":
        _emit([server.model_dump(mode="json") for server in list_server_definitions()], args.json)
        return 0

    if args.command == "describe-mcp-server":
        _emit(get_server_definition(args.server).model_dump(mode="json"), args.json)
        return 0

    if args.command == "validate-mcp-config":
        servers = list_server_definitions()
        _emit({"status": "valid", "servers": len(servers), "transport": "stdio"}, args.json)
        return 0

    if args.command == "mcp-get-case":
        client = BoundedMCPClient()
        _emit(client.call_tool("case-data", "get_case", {"case_id": args.case_id}), args.json)
        return 0

    if args.command == "mcp-assess-case":
        client = BoundedMCPClient()
        _emit(
            client.call_tool("pathway-rules", "run_pathway_assessment", {"case_id": args.case_id}),
            args.json,
        )
        return 0

    if args.command == "mcp-search-evidence":
        client = BoundedMCPClient()
        _emit(
            client.call_tool(
                "policy-evidence",
                "search_evidence",
                {"pathway_code": args.pathway_code, "query": args.query},
            ),
            args.json,
        )
        return 0

    if args.command == "list-skills":
        _emit([skill.model_dump(mode="json") for skill in list_skill_definitions()], args.json)
        return 0

    if args.command == "describe-skill":
        skill_matches = [skill for skill in list_skill_definitions() if skill.name == args.skill]
        if not skill_matches:
            raise ValueError(f"unknown skill: {args.skill}")
        _emit(skill_matches[0].model_dump(mode="json"), args.json)
        return 0

    if args.command == "run-skill":
        _emit(execute_skill(args.skill, args.case_id).model_dump(mode="json"), args.json)
        return 0

    if args.command == "guardrail-check-input":
        guardrail_result = GuardrailService().check_text(args.text)
        _emit(guardrail_result.model_dump(mode="json"), args.json)
        return 0 if guardrail_result.passed else 2

    if args.command == "guardrail-check-case":
        case = get_case_by_id(args.case_id)
        guardrail_result = GuardrailService().check_case_payload(case.model_dump(mode="json"))
        _emit(guardrail_result.model_dump(mode="json"), args.json)
        return 0 if guardrail_result.passed else 2

    if args.command == "guardrail-check-evidence":
        evidence_matches = [
            item for item in load_local_evidence() if item.evidence_id == args.evidence_id
        ]
        if not evidence_matches:
            raise ValueError(f"unknown evidence_id: {args.evidence_id}")
        guardrail_result = GuardrailService().check_evidence(evidence_matches[0])
        _emit(guardrail_result.model_dump(mode="json"), args.json)
        return 0 if guardrail_result.passed else 2

    if args.command == "prepare-review":
        record = HumanReviewService().prepare_review(args.case_id, ExecutionMode(args.mode))
        _emit(record.model_dump(mode="json"), args.json)
        return 0

    if args.command == "list-reviews":
        records = ReviewStore().list_records()
        _emit([record.model_dump(mode="json") for record in records], args.json)
        return 0

    if args.command == "show-review":
        record = ReviewStore().load(args.review_id)
        _emit(record.model_dump(mode="json"), args.json)
        return 0

    if args.command == "decide-review":
        decision = HumanReviewDecision(args.decision.upper())
        amendments = (
            load_amendments_from_file(Path(args.amendment_file)) if args.amendment_file else []
        )
        record = HumanReviewService().decide(
            review_id=args.review_id,
            decision=decision,
            reviewer_id=args.reviewer_id,
            comments=args.comments,
            reason=args.reason,
            amendments=amendments,
        )
        _emit(record.model_dump(mode="json"), args.json)
        return 0

    if args.command == "verify-review-integrity":
        integrity_result = HumanReviewService().verify_integrity(args.review_id)
        _emit(integrity_result, args.json)
        return 0 if integrity_result["valid"] else 2

    if args.command == "run-security-evaluation":
        summary = run_security_evaluation()
        _emit(summary.model_dump(mode="json"), args.json)
        return 0 if summary.false_negatives == 0 else 2

    if args.command == "list-benchmark-cases":
        cases = load_benchmark_cases()
        _emit([case.model_dump(mode="json") for case in cases], args.json)
        return 0

    if args.command == "show-benchmark-case":
        matches = [case for case in load_benchmark_cases() if case.case_id == args.case_id]
        if not matches:
            raise ValueError(f"unknown benchmark case: {args.case_id}")
        _emit(matches[0].model_dump(mode="json"), args.json)
        return 0

    if args.command == "validate-benchmark":
        _emit(validate_benchmark(), args.json)
        return 0

    if args.command == "evaluate-deterministic":
        deterministic_result = evaluate_deterministic()
        _emit(deterministic_result.model_dump(mode="json"), args.json)
        return 0 if deterministic_result.failed_count == 0 else 2

    if args.command == "evaluate-agents":
        agent_result = evaluate_agents(ExecutionMode(args.mode))
        _emit(agent_result.model_dump(mode="json"), args.json)
        return 0 if agent_result.failed_count == 0 else 2

    if args.command == "evaluate-skills":
        skill_result = evaluate_skills()
        _emit(skill_result.model_dump(mode="json"), args.json)
        return 0 if skill_result.failed_count == 0 else 2

    if args.command == "evaluate-evidence":
        evidence_result = evaluate_evidence()
        _emit(evidence_result.model_dump(mode="json"), args.json)
        return 0 if evidence_result.failed_count == 0 else 2

    if args.command == "evaluate-reviews":
        review_result = evaluate_reviews()
        _emit(review_result.model_dump(mode="json"), args.json)
        return 0 if review_result.failed_count == 0 else 2

    if args.command == "evaluate-reproducibility":
        reproducibility_result = evaluate_reproducibility()
        _emit(reproducibility_result.model_dump(mode="json"), args.json)
        return 0 if reproducibility_result.failed_count == 0 else 2

    if args.command == "run-full-evaluation":
        report, output_dir = run_full_evaluation()
        payload = report.model_dump(mode="json")
        payload["output_dir"] = str(output_dir)
        _emit(payload, args.json)
        return 0 if not report.failed_case_ids else 2

    if args.command == "show-evaluation-summary":
        run_dir = ARTIFACT_ROOT / args.run_id
        if args.json:
            _emit(read_json(run_dir / "evaluation-report.json"), True)
        else:
            print((run_dir / "evaluation-summary.md").read_text(encoding="utf-8"))
        return 0

    if args.command == "ui-info":
        config = load_ui_config()
        evidence = load_evaluation_evidence()
        ui_payload: dict[str, Any] = {
            "title": config.title,
            "default_execution_mode": config.default_execution_mode.value,
            "public_modes": [mode.value for mode in available_public_modes(config)],
            "live_mode_enabled": config.enable_live_mode,
            "review_store_path": str(config.review_store_path),
            "environment_label": config.environment_label,
            "presentation_mode": config.presentation_mode,
            "safety_banner": SAFETY_BANNER,
            "synthetic_case_count": len(list_case_options()),
            "evaluation_run_id": evidence["benchmark"]["run_id"],
            "demonstration_only": True,
        }
        _emit(ui_payload, args.json)
        return 0

    raise ValueError(f"Unsupported command: {args.command}")


def _emit(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                print(" | ".join(f"{key}: {value}" for key, value in item.items()))
            else:
                print(item)
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            print(f"{key}: {value}")
        return
    print(payload)


def _write_artifact(case_id: str, content: str) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_DIR / f"{case_id}.json").write_text(content + "\n", encoding="utf-8")


def _risk_model_description() -> dict[str, Any]:
    return {
        "score_range": "0-10",
        "risk_levels": {
            "LOW": "0-2",
            "MODERATE": "3-4",
            "HIGH": "5-6",
            "CRITICAL": "7-10",
        },
        "factor_codes": [
            "BREACH_SEVERITY",
            "TARGET_CONSUMPTION",
            "PRIORITY",
            "MISSING_NEXT_EVENT",
            "NEXT_EVENT_AFTER_TARGET",
            "OPERATIONAL_FLAGS",
            "SUBSTANTIAL_BREACH",
            "TIME_SENSITIVE_CATEGORY",
        ],
        "examples": {
            "2.0": assign_risk_level(2.0).value,
            "4.0": assign_risk_level(4.0).value,
            "6.0": assign_risk_level(6.0).value,
            "7.0": assign_risk_level(7.0).value,
        },
        "warning": "Risk is operational and deterministic, not clinical.",
        "human_review_required": True,
    }


if __name__ == "__main__":
    raise SystemExit(main())
