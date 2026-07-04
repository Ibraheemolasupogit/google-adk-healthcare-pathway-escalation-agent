"""Tests for modules that intentionally remain placeholders in Milestone 2."""

from __future__ import annotations

from typing import cast

import pytest
from agents import (
    CoordinatorAgent,
    EscalationAgent,
    EvidenceAgent,
    PathwayAgent,
    ReviewAgent,
    RiskAgent,
)
from app.config import AppConfig
from evaluation.evaluator import run_evaluation
from mcp_servers.case_data_server import create_case_data_server
from mcp_servers.pathway_rules_server import create_pathway_rules_server
from mcp_servers.policy_evidence_server import create_policy_evidence_server
from schemas.assessment import PathwayAssessment
from schemas.case import SyntheticPathwayCase
from schemas.escalation import EscalationRecommendation
from security.input_guardrails import validate_synthetic_input
from security.output_validation import validate_escalation_output
from tools.case_tools import load_synthetic_cases
from tools.evidence_tools import search_policy_evidence
from tools.pathway_tools import get_pathway_rule


def test_app_config_reports_milestone_2() -> None:
    config = AppConfig()

    assert config.milestone == "Milestone 2"
    assert config.functional_agent_execution_enabled is False


def test_agent_placeholders_raise_not_implemented() -> None:
    case = load_synthetic_cases()[0]
    rule = get_pathway_rule(case.pathway_code)
    assessment = PathwayAssessment.model_construct(
        case_id=case.case_id,
        pathway_code=rule.pathway_code,
        pathway_name=rule.pathway_name,
    )

    with pytest.raises(NotImplementedError):
        CoordinatorAgent().assess_case(case)
    with pytest.raises(NotImplementedError):
        PathwayAgent().assess_pathway(case)
    with pytest.raises(NotImplementedError):
        RiskAgent().calculate_risk(case)
    with pytest.raises(NotImplementedError):
        EvidenceAgent().retrieve_evidence(case)
    with pytest.raises(NotImplementedError):
        EscalationAgent().generate_draft(assessment)
    with pytest.raises(NotImplementedError):
        ReviewAgent().validate_for_review(cast(EscalationRecommendation, object()))


def test_non_network_placeholder_modules_raise_not_implemented() -> None:
    case: SyntheticPathwayCase = load_synthetic_cases()[0]

    with pytest.raises(NotImplementedError):
        create_case_data_server()
    with pytest.raises(NotImplementedError):
        create_pathway_rules_server()
    with pytest.raises(NotImplementedError):
        create_policy_evidence_server()
    with pytest.raises(NotImplementedError):
        run_evaluation()
    with pytest.raises(NotImplementedError):
        validate_synthetic_input(case)
    with pytest.raises(NotImplementedError):
        validate_escalation_output(cast(EscalationRecommendation, object()))
    with pytest.raises(NotImplementedError):
        search_policy_evidence("synthetic query")
