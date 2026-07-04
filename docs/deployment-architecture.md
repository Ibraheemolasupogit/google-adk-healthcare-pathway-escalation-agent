# Deployment Architecture

Milestone 7 packages the Streamlit UI for Cloud Run-compatible container deployment.

```text
Browser
  -> Streamlit UI
  -> UI service layer
  -> deterministic assessment service
  -> Google ADK mock/mock-MCP orchestration
  -> local MCP-compatible capabilities
  -> controlled local evidence
  -> guardrails
  -> runtime human-review store
```

The container runs as a non-root user, reads the Cloud Run `PORT` variable and defaults to `mock-mcp`. Runtime review files remain under ignored `artifacts/` storage.

No Cloud Run deployment is performed in this milestone.

