"""Google ADK coordinator agent definition."""

from google.adk.agents import Agent
from tools.adk_tools import build_adk_tools

from agents.registry import AGENT_MODEL_PLACEHOLDER, load_instruction

RESPONSIBILITY = "Coordinate specialist agents and enforce deterministic review-gated output."


def create_coordinator_agent() -> Agent:
    """Create the ADK coordinator agent definition."""
    return Agent(
        name="coordinator_agent",
        model=AGENT_MODEL_PLACEHOLDER,
        description=RESPONSIBILITY,
        instruction=load_instruction("coordinator.md"),
        tools=build_adk_tools(),
    )
