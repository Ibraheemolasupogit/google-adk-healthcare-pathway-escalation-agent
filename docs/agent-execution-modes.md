# Agent Execution Modes

## Deterministic Mode

Use existing Milestone 2 commands such as `assess-case` and `assess-all`. No model or ADK workflow is required.

## Mock Mode

`agent-assess --mode mock` uses ADK agent definitions, deterministic tools, local evidence, structured drafts and review validation without any external API calls. Model metadata is explicitly labelled as mock.

## Mock MCP Mode

`agent-assess --mode mock-mcp` exercises the approved local MCP servers through the bounded in-memory adapter. It requires no Gemini credentials and preserves deterministic values.

Milestone 6 evaluates both mock modes with:

```bash
python3 -m app.main evaluate-agents --mode mock --json
python3 -m app.main evaluate-agents --mode mock-mcp --json
```

`run-full-evaluation` also checks execution-mode parity for deterministic fields across direct, mock and mock-MCP paths.

## Streamlit UI Default

The Milestone 7 public demonstration UI defaults to `mock-mcp`. Live mode is disabled by default and is not exposed unless separately configured with secure credentials.

## Review Preparation

`prepare-review --mode mock-mcp` runs the selected execution mode, validates the draft with guardrails, and creates a local `PENDING` human-review record. Approval is never automatic and requires a separate `decide-review` command.

## Live Mode

`agent-assess --mode live` requires valid Google configuration. Missing credentials fail safely and do not print secrets. Live Gemini execution should only be attempted intentionally in an environment configured for external model calls.

All modes preserve deterministic values and require human review. `live-mcp` is schema-defined for future use but not used by automated tests.
