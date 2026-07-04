"""Configuration placeholders for future Google and runtime settings."""

from pydantic import BaseModel


class AppConfig(BaseModel):
    """Non-secret configuration values for the Milestone 1 placeholder app."""

    project_name: str = "NHS Pathway Escalation and Evidence Agent"
    milestone: str = "Milestone 3"
    functional_agent_execution_enabled: bool = False
