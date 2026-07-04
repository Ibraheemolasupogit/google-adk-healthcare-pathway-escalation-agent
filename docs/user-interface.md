# User Interface

Milestone 7 adds a Streamlit demonstration interface at `ui/streamlit_app.py`.

Run locally:

```bash
streamlit run ui/streamlit_app.py
```

The UI defaults to `mock-mcp`, uses synthetic cases only and does not require Gemini credentials. It displays deterministic assessment values, ADK workflow summaries, MCP/tool calls, controlled evidence, guardrail status, human-review records and committed Milestone 6 evaluation evidence.

No free-text patient case entry is provided. Reviewer aliases are demonstration aliases only and are not authenticated identity.

## Sections

- Overview
- Select Case
- Deterministic Assessment
- Agent Workflow
- Evidence
- Security and Guardrails
- Human Review
- Evaluation Evidence
- Architecture and Limitations

## Presentation Mode

Set `DEMO_PRESENTATION_MODE=true` to select the primary demo case and hide less relevant choices for screenshot or video preparation.

