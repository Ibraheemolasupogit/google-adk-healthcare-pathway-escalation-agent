"""Safe UI configuration for the Streamlit demonstration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from schemas.agent import ExecutionMode

APP_TITLE = "NHS Pathway Escalation and Evidence Agent"
APP_SUBTITLE = (
    "A synthetic, evidence-grounded Google ADK demonstration for operational pathway review."
)
SAFETY_BANNER = (
    "This application uses synthetic demonstration data only. It does not provide clinical "
    "advice, make clinical decisions, submit escalations or connect to live NHS systems."
)
CLINICAL_DISCLAIMER = (
    "Demonstration pathway targets are not operational NHS guidance. Outputs require human "
    "review and have no clinical or operational authority."
)
PRIMARY_DEMO_CASE_ID = "SYN-CANCER-62-003"
PRESENTATION_MODE_ENV = "DEMO_PRESENTATION_MODE"
DEFAULT_REVIEW_STORE = Path("artifacts") / "ui-reviews"
EVIDENCE_ROOT = Path("docs") / "evidence" / "milestone-6"


@dataclass(frozen=True)
class UIConfig:
    """Non-secret UI settings."""

    title: str = APP_TITLE
    subtitle: str = APP_SUBTITLE
    default_execution_mode: ExecutionMode = ExecutionMode.MOCK_MCP
    review_store_path: Path = DEFAULT_REVIEW_STORE
    enable_live_mode: bool = False
    max_displayed_audit_steps: int = 12
    max_evidence_records: int = 5
    environment_label: str = "local-demonstration"
    presentation_mode: bool = False


def load_ui_config() -> UIConfig:
    """Load safe UI settings from environment variables."""
    default_mode = os.getenv("APP_DEFAULT_EXECUTION_MODE", ExecutionMode.MOCK_MCP.value)
    if default_mode not in {ExecutionMode.MOCK.value, ExecutionMode.MOCK_MCP.value}:
        default_mode = ExecutionMode.MOCK_MCP.value
    return UIConfig(
        title=os.getenv("APP_UI_TITLE", APP_TITLE),
        default_execution_mode=ExecutionMode(default_mode),
        review_store_path=Path(os.getenv("APP_REVIEW_STORE_PATH", str(DEFAULT_REVIEW_STORE))),
        enable_live_mode=os.getenv("APP_ENABLE_LIVE_MODE", "false").lower() == "true",
        max_displayed_audit_steps=int(os.getenv("APP_MAX_AUDIT_STEPS", "12")),
        max_evidence_records=int(os.getenv("APP_MAX_EVIDENCE_RECORDS", "5")),
        environment_label=os.getenv("APP_ENVIRONMENT_LABEL", "local-demonstration"),
        presentation_mode=os.getenv(PRESENTATION_MODE_ENV, "false").lower() == "true",
    )


def available_public_modes(config: UIConfig) -> list[ExecutionMode]:
    """Return execution modes that may be selected in the public UI."""
    modes = [ExecutionMode.MOCK_MCP, ExecutionMode.MOCK]
    if config.enable_live_mode:
        modes.append(ExecutionMode.LIVE)
    return modes
