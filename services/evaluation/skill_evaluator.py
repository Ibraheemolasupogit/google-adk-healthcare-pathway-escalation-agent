"""Agent Skill evaluator."""

from __future__ import annotations

from datetime import UTC, datetime

from schemas.evaluation import EvaluationFailure, SkillEvaluationResult
from tools.case_tools import load_synthetic_cases

from services.assessment_service import assess_case
from services.evaluation.common import failure, metric, suite_result
from services.skill_executor import execute_skill, list_skill_definitions


def evaluate_skills() -> SkillEvaluationResult:
    """Evaluate approved local skills on existing synthetic case IDs."""
    started = datetime.now(UTC)
    cases = load_synthetic_cases()
    skills = [skill.name for skill in list_skill_definitions()]
    failures: list[EvaluationFailure] = []
    total = len(cases) * len(skills)
    load_ok = input_ok = output_ok = preserved = 0
    for case in cases:
        expected = assess_case(case)
        for skill_name in skills:
            try:
                result = execute_skill(skill_name, case.case_id)
                load_ok += 1
                input_ok += 1
                if result.success and result.human_review_required and result.demonstration_only:
                    output_ok += 1
                else:
                    failures.append(
                        failure(case.case_id, skill_name, True, False, "bad skill flags")
                    )
                if skill_name == "calculate_risk":
                    if result.output["risk_score"] == expected.risk_score:
                        preserved += 1
                    else:
                        failures.append(
                            failure(
                                case.case_id,
                                "skill_risk_score",
                                expected.risk_score,
                                result.output["risk_score"],
                                "skill changed risk score",
                            )
                        )
                else:
                    preserved += 1
            except Exception as exc:
                failures.append(
                    failure(case.case_id, skill_name, "success", str(exc), "skill failed")
                )
    metrics = [
        metric("skill_load_rate", load_ok / total, 1.0),
        metric("input_validation_rate", input_ok / total, 1.0),
        metric("output_validation_rate", output_ok / total, 1.0),
        metric("deterministic_preservation_rate", preserved / total, 1.0),
    ]
    return SkillEvaluationResult.model_validate(
        suite_result(
            started_at=started,
            case_count=total,
            failures=failures,
            metrics=metrics,
            execution_mode="skills",
        ).model_dump()
    )
