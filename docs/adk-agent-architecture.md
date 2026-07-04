# ADK Agent Architecture

Milestone 3 defines six Google ADK agents using `google-adk` 1.36.0:

- Coordinator Agent
- Pathway Agent
- Risk Agent
- Evidence Agent
- Escalation Agent
- Review Agent

Each agent is built with `google.adk.agents.Agent` and controlled `FunctionTool` wrappers around local deterministic services. The deterministic Milestone 2 engine remains the source of truth for targets, elapsed time, breach status, risk score, risk level, risk factors and recommended operational actions.

Mock execution mode exercises the same schemas, tools and review process without calling Gemini. Live mode is configuration-gated and must not run without credentials.

No functional MCP network services, frontend or deployment are implemented in this milestone.
