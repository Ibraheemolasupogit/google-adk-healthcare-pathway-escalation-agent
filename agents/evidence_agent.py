"""Google ADK evidence agent definition."""

from google.adk.agents import Agent
from tools.adk_tools import build_adk_tools

from agents.registry import AGENT_MODEL_PLACEHOLDER, load_instruction

RESPONSIBILITY = "Retrieve local demonstration evidence and source metadata."


def create_evidence_agent() -> Agent:
    """Create the ADK evidence agent definition."""
    return Agent(
        name="evidence_agent",
        model=AGENT_MODEL_PLACEHOLDER,
        description=RESPONSIBILITY,
        instruction=load_instruction("evidence.md"),
        tools=build_adk_tools(),
    )
