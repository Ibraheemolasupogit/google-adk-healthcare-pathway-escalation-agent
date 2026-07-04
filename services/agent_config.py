"""Configuration helpers for Milestone 3 ADK orchestration."""

from __future__ import annotations

import importlib.metadata
import os
from dataclasses import dataclass

from schemas.agent import ExecutionMode
from tools.exceptions import DomainValidationError

DEFAULT_MODEL = "gemini-2.5-flash"


@dataclass(frozen=True)
class AgentRuntimeConfig:
    """Runtime configuration for ADK-backed orchestration."""

    execution_mode: ExecutionMode
    model_name: str
    google_adk_version: str
    google_cloud_project_configured: bool
    google_cloud_location_configured: bool
    google_api_key_configured: bool
    vertexai_flag_configured: bool

    @property
    def live_ready(self) -> bool:
        """Return whether enough Google configuration is present for live mode."""
        if self.vertexai_flag_configured:
            return self.google_cloud_project_configured and self.google_cloud_location_configured
        return self.google_api_key_configured


def load_agent_runtime_config(mode: ExecutionMode) -> AgentRuntimeConfig:
    """Load non-secret agent runtime configuration from environment variables."""
    return AgentRuntimeConfig(
        execution_mode=mode,
        model_name=os.getenv("GOOGLE_GENAI_MODEL", DEFAULT_MODEL),
        google_adk_version=get_google_adk_version(),
        google_cloud_project_configured=bool(os.getenv("GOOGLE_CLOUD_PROJECT")),
        google_cloud_location_configured=bool(os.getenv("GOOGLE_CLOUD_LOCATION")),
        google_api_key_configured=bool(os.getenv("GOOGLE_API_KEY")),
        vertexai_flag_configured=os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower()
        in {"1", "true", "yes"},
    )


def validate_live_configuration(config: AgentRuntimeConfig) -> None:
    """Fail safely when live Gemini-backed execution is not configured."""
    if config.execution_mode != ExecutionMode.LIVE:
        return
    if not config.live_ready:
        raise DomainValidationError(
            "Live mode requires GOOGLE_API_KEY or Vertex AI project/location configuration. "
            "No secret values were read or printed."
        )


def get_google_adk_version() -> str:
    """Return the installed Google ADK package version."""
    try:
        return importlib.metadata.version("google-adk")
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"
