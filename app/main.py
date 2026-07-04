"""Deterministic command-line interface for Milestone 2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from services.assessment_service import assess_case, assess_cases
from services.risk_engine import assign_risk_level
from tools.case_tools import get_case_by_id, load_synthetic_cases
from tools.exceptions import CaseNotFoundError, DomainValidationError, PathwayRuleNotFoundError
from tools.pathway_tools import load_pathway_rules

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
