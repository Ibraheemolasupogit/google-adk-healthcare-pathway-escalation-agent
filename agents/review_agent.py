"""Google ADK review agent definition."""

from google.adk.agents import Agent
from tools.adk_tools import build_adk_tools

from agents.registry import AGENT_MODEL_PLACEHOLDER, load_instruction

RESPONSIBILITY = "Validate draft safety, schema compliance and human-review controls."


def create_review_agent() -> Agent:
    """Create the ADK review agent definition."""
    return Agent(
        name="review_agent",
        model=AGENT_MODEL_PLACEHOLDER,
        description=RESPONSIBILITY,
        instruction=load_instruction("review.md"),
        tools=build_adk_tools(),
    )
