"""Session-state keys and reset helpers for Streamlit."""

from __future__ import annotations

from typing import Any

UI_STATE_KEYS = {
    "selected_case_id",
    "deterministic_result",
    "agent_result",
    "review_id",
    "review_record",
}


def reset_case_state(state: Any, case_id: str) -> None:
    """Reset non-sensitive state when the selected synthetic case changes."""
    previous = state.get("selected_case_id")
    if previous == case_id:
        return
    for key in UI_STATE_KEYS - {"selected_case_id"}:
        state.pop(key, None)
    state["selected_case_id"] = case_id
