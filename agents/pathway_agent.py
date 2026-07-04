"""Google ADK pathway agent definition."""

from google.adk.agents import Agent
from tools.adk_tools import build_adk_tools

from agents.registry import AGENT_MODEL_PLACEHOLDER, load_instruction

RESPONSIBILITY = "Retrieve controlled pathway rules and deterministic breach status."


def create_pathway_agent() -> Agent:
    """Create the ADK pathway agent definition."""
    return Agent(
        name="pathway_agent",
        model=AGENT_MODEL_PLACEHOLDER,
        description=RESPONSIBILITY,
        instruction=load_instruction("pathway.md"),
        tools=build_adk_tools(),
    )
