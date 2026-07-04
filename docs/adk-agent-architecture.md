# ADK Agent Architecture

Milestone 3 defines six Google ADK agents using `google-adk` 1.36.0:

- Coordinator Agent
- Pathway Agent
- Risk Agent
- Evidence Agent
- Escalation Agent
- Review Agent

Each agent is built with `google.adk.agents.Agent` and controlled `FunctionTool` wrappers around local deterministic services. The deterministic Milestone 2 engine remains the source of truth for targets, elapsed time, breach status, risk score, risk level, risk factors and recommended operational actions.

Mock execution mode exercises the same schemas, tools and review process without calling Gemini. `mock-mcp` mode routes case, pathway and evidence access through the bounded local MCP client so the ADK workflow can validate server boundaries while preserving deterministic outputs. Live mode is configuration-gated and must not run without credentials.

Milestone 5 adds a central guardrail pass after draft generation. The automated Review Agent remains a safety and consistency reviewer only; it cannot create human approval. Human decisions are recorded by the separate backend Human Review Service.

Milestone 6 evaluates mock and mock-MCP agent execution over the synthetic benchmark. The evaluator checks valid structured output, deterministic preservation, local evidence grounding, unsupported-claim avoidance, prohibited-language avoidance and human-review enforcement.

Milestone 7 exposes mock and mock-MCP execution in the Streamlit demonstration UI. The public default is `mock-mcp`; the UI does not imply that mock output came from Gemini.

Actual Cloud Run deployment, live Gemini validation and autonomous escalation are not implemented in this milestone.
