# Agent Execution Modes

## Deterministic Mode

Use existing Milestone 2 commands such as `assess-case` and `assess-all`. No model or ADK workflow is required.

## Mock Mode

`agent-assess --mode mock` uses ADK agent definitions, deterministic tools, local evidence, structured drafts and review validation without any external API calls. Model metadata is explicitly labelled as mock.

## Live Mode

`agent-assess --mode live` requires valid Google configuration. Missing credentials fail safely and do not print secrets. Live Gemini execution should only be attempted intentionally in an environment configured for external model calls.

All modes preserve deterministic values and require human review.
