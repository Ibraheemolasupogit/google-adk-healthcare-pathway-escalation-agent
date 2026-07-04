"""Google ADK escalation agent definition."""

from google.adk.agents import Agent
from tools.adk_tools import build_adk_tools

from agents.registry import AGENT_MODEL_PLACEHOLDER, load_instruction

RESPONSIBILITY = "Draft structured non-clinical operational escalation content."


def create_escalation_agent() -> Agent:
    """Create the ADK escalation agent definition."""
    return Agent(
        name="escalation_agent",
        model=AGENT_MODEL_PLACEHOLDER,
        description=RESPONSIBILITY,
        instruction=load_instruction("escalation.md"),
        tools=build_adk_tools(),
    )
