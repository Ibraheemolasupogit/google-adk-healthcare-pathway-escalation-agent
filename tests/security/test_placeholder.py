"""Security-oriented tests for Milestone 1 constraints."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_env_example_contains_placeholders_only() -> None:
    """Environment example should list empty placeholders only."""
    env_example = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8").splitlines()

    assert env_example == [
        "GOOGLE_API_KEY=",
        "GOOGLE_CLOUD_PROJECT=",
        "GOOGLE_CLOUD_LOCATION=",
        "GOOGLE_GENAI_USE_VERTEXAI=",
    ]


def test_threat_model_covers_required_threats() -> None:
    """Threat model should mention the required Milestone 1 threat categories."""
    content = (PROJECT_ROOT / "security" / "threat_model.md").read_text(encoding="utf-8")

    required_phrases = [
        "Accidental Use of Personal Data",
        "Prompt Injection",
        "Malicious Retrieved Content",
        "Unsupported Pathway Claims",
        "Hallucinated Evidence",
        "Excessive Tool Permissions",
        "Secret Exposure",
        "Unsafe Autonomous Escalation",
        "Audit-Log Leakage",
        "Denial-of-Service Through Oversized Inputs",
    ]

    for phrase in required_phrases:
        assert phrase in content
