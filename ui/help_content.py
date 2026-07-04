"""Fixed public help and architecture content for the Streamlit UI."""

from __future__ import annotations

BADGES = [
    "Agents for Good",
    "Google ADK",
    "MCP",
    "Agent Skills",
    "Human in the Loop",
    "Synthetic Data Only",
    "Demonstration Only",
]

WORKFLOW_STEPS = [
    "User",
    "Coordinator Agent",
    "Pathway Agent",
    "Risk Agent",
    "Evidence Agent",
    "Escalation Agent",
    "Review Agent",
    "Human Reviewer",
]

LIMITATIONS = [
    "Synthetic data only.",
    "Demonstration pathway targets, not operational NHS guidance.",
    "No clinical authority, diagnosis, treatment advice or medication advice.",
    "No live NHS integration.",
    "No authenticated reviewer identity.",
    "Mock and mock-MCP modes do not call Gemini.",
    "Deterministic guardrails are not exhaustive.",
    "Local hashes are tamper-evident checks, not digital signatures.",
    "Production use would require governance, security and operational validation.",
]

ARCHITECTURE_SUMMARY = {
    "Agents": "Coordinator, Pathway, Risk, Evidence, Escalation and Review agents.",
    "MCP": "Local case-data, pathway-rules and policy-evidence capabilities.",
    "Skills": "identify_pathway, calculate_risk, retrieve_evidence and generate_escalation.",
    "Guardrails": (
        "Prompt injection, personal data, secret, deterministic-integrity and review checks."
    ),
    "Review": "Backend prepare, approve, amend, reject and integrity verification.",
}
