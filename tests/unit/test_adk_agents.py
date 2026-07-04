"""Unit tests for Milestone 3 ADK agent definitions and remaining placeholders."""

from __future__ import annotations

from typing import cast

import pytest
from agents import build_agent_registry, describe_agents
from app.config import AppConfig
from evaluation.evaluator import run_evaluation
from google.adk.agents import Agent
from schemas.agent import AgentName
from schemas.case import SyntheticPathwayCase
from schemas.escalation import EscalationRecommendation
from security.input_guardrails import validate_synthetic_input
from security.output_validation import validate_escalation_output
from tools.case_tools import load_synthetic_cases
from tools.evidence_tools import search_policy_evidence


def test_app_config_reports_milestone_3() -> None:
    config = AppConfig()

    assert config.milestone == "Milestone 3"
    assert config.functional_agent_execution_enabled is False


def test_adk_agent_definitions_initialise() -> None:
    registry = build_agent_registry()

    assert set(registry) == set(AgentName)
    assert all(isinstance(agent, Agent) for agent in registry.values())
    assert all(agent.description for agent in registry.values())
    assert all(agent.instruction for agent in registry.values())
    assert all(agent.tools for agent in registry.values())


def test_every_agent_has_defined_responsibility() -> None:
    descriptions = describe_agents()

    assert len(descriptions) == 6
    assert {item["agent_name"] for item in descriptions} == {name.value for name in AgentName}
    assert all(item["responsibility"] for item in descriptions)


def test_non_network_placeholder_modules_still_raise_not_implemented() -> None:
    case: SyntheticPathwayCase = load_synthetic_cases()[0]

    with pytest.raises(NotImplementedError):
        run_evaluation()
    with pytest.raises(NotImplementedError):
        validate_synthetic_input(case)
    with pytest.raises(NotImplementedError):
        validate_escalation_output(cast(EscalationRecommendation, object()))
    with pytest.raises(NotImplementedError):
        search_policy_evidence("synthetic query")
