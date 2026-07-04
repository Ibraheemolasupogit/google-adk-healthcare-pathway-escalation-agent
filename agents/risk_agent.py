"""Google ADK risk agent definition."""

from google.adk.agents import Agent
from tools.adk_tools import build_adk_tools

from agents.registry import AGENT_MODEL_PLACEHOLDER, load_instruction

RESPONSIBILITY = "Explain deterministic operational risk without recalculating it."


def create_risk_agent() -> Agent:
    """Create the ADK risk agent definition."""
    return Agent(
        name="risk_agent",
        model=AGENT_MODEL_PLACEHOLDER,
        description=RESPONSIBILITY,
        instruction=load_instruction("risk.md"),
        tools=build_adk_tools(),
    )
