"""Registry for Milestone 3 Google ADK agent definitions."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from google.adk.agents import Agent
from schemas.agent import AgentName

AGENT_MODEL_PLACEHOLDER = "gemini-2.5-flash"
INSTRUCTION_DIR = Path(__file__).resolve().parent / "instructions"


def load_instruction(filename: str) -> str:
    """Load a maintainable agent instruction file."""
    return (INSTRUCTION_DIR / filename).read_text(encoding="utf-8")


def build_agent_registry() -> dict[AgentName, Agent]:
    """Create all ADK specialist agent definitions."""
    from agents.coordinator import create_coordinator_agent
    from agents.escalation_agent import create_escalation_agent
    from agents.evidence_agent import create_evidence_agent
    from agents.pathway_agent import create_pathway_agent
    from agents.review_agent import create_review_agent
    from agents.risk_agent import create_risk_agent

    factories: dict[AgentName, Callable[[], Agent]] = {
        AgentName.COORDINATOR: create_coordinator_agent,
        AgentName.PATHWAY: create_pathway_agent,
        AgentName.RISK: create_risk_agent,
        AgentName.EVIDENCE: create_evidence_agent,
        AgentName.ESCALATION: create_escalation_agent,
        AgentName.REVIEW: create_review_agent,
    }
    return {name: factory() for name, factory in factories.items()}


def describe_agents() -> list[dict[str, str]]:
    """Return concise agent responsibility descriptions."""
    return [
        {"agent_name": name.value, "responsibility": agent.description}
        for name, agent in build_agent_registry().items()
    ]
