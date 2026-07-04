"""Unit tests for reusable local Agent Skills."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from schemas.agent import ExecutionMode
from schemas.mcp import SkillExecutionResult
from services.assessment_service import assess_case
from services.skill_executor import (
    APPROVED_SKILLS,
    MAX_SKILL_STEPS,
    SkillExecutor,
    SkillRegistry,
    execute_skill,
    list_skill_definitions,
)
from tools.case_tools import get_case_by_id
from tools.exceptions import DomainValidationError

CASE_ID = "SYN-CANCER-2WW-001"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_skill_registry_loads_only_approved_metadata() -> None:
    definitions = list_skill_definitions()

    assert {definition.name for definition in definitions} == APPROVED_SKILLS
    assert all(definition.demonstration_only is True for definition in definitions)
    assert all(definition.human_review_required is True for definition in definitions)
    with pytest.raises(DomainValidationError, match="unknown skill"):
        SkillRegistry().get_skill("external")


def test_skill_metadata_references_existing_schemas_and_examples() -> None:
    for definition in list_skill_definitions():
        skill_root = PROJECT_ROOT / "skills" / definition.name
        assert (skill_root / definition.input_schema_path).exists()
        assert (skill_root / definition.output_schema_path).exists()
        examples = json.loads((skill_root / "examples.json").read_text(encoding="utf-8"))
        assert examples


def test_identify_pathway_skill_uses_controlled_pathway_rule() -> None:
    result = execute_skill("identify_pathway", CASE_ID)

    assert result.execution_mode == ExecutionMode.MOCK_MCP
    assert result.output["case_id"] == CASE_ID
    assert result.output["pathway_code"] == "CANCER_2WW"
    assert result.output["target"] > 0
    assert result.validation.valid is True
    assert len(result.steps) == 2
    assert len(result.mcp_invocations) == 2
    SkillExecutionResult.model_validate(result.model_dump())


def test_calculate_risk_skill_preserves_deterministic_score() -> None:
    result = execute_skill("calculate_risk", CASE_ID)
    direct = assess_case(get_case_by_id(CASE_ID))

    assert result.output["risk_score"] == direct.risk_score
    assert result.output["breach_status"] == direct.breach_status.value
    assert result.output["human_review_required"] is True
    assert result.human_review_required is True
    assert result.success is True


def test_retrieve_evidence_skill_returns_demonstration_only_evidence() -> None:
    result = execute_skill("retrieve_evidence", CASE_ID)

    assert result.output["demonstration_only"] is True
    assert result.output["evidence"]
    assert all(item["demonstration_only"] is True for item in result.output["evidence"])
    assert len(result.steps) == 2


def test_generate_escalation_skill_never_submits_and_requires_review() -> None:
    result = execute_skill("generate_escalation", CASE_ID)

    assert result.output["submitted"] is False
    assert result.output["human_review_required"] is True
    assert result.output["review_status"] == "PENDING"
    assert result.human_review_required is True
    assert result.demonstration_only is True


def test_skill_execution_rejects_unknown_skill_and_step_limit() -> None:
    with pytest.raises(DomainValidationError, match="unknown skill"):
        execute_skill("external", CASE_ID)

    executor = SkillExecutor()
    executor.steps = [
        execute_skill("calculate_risk", CASE_ID).steps[0] for _ in range(MAX_SKILL_STEPS)
    ]
    with pytest.raises(DomainValidationError, match="maximum skill step limit"):
        executor.execute("calculate_risk", CASE_ID)
