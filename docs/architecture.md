# Architecture

## Milestone 2 Status

This document describes the planned architecture and the implemented deterministic domain layer. The repository now implements local case validation, pathway-rule loading, elapsed-time calculation, breach classification, operational risk scoring, recommended actions, audit traces, Google ADK mock orchestration, local MCP-compatible server adapters, reusable Agent Skill metadata and CLI commands. Live Gemini calls, frontend review UI and deployment remain planned.

## Planned Components

- **User or reviewer interface:** future UI or CLI for submitting synthetic cases and reviewing drafts.
- **Coordinator agent:** controls workflow, delegates tasks, assembles draft outputs, and enforces review routing.
- **Pathway agent:** identifies pathway type and retrieves the applicable target.
- **Risk agent:** performs deterministic target, breach, and explainable risk calculations.
- **Evidence agent:** retrieves controlled evidence and source metadata.
- **Escalation agent:** creates structured draft recommendations.
- **Review agent:** validates completeness, unsupported claims, schema compliance, safety, and human-approval state.
- **Case-data tools and MCP server:** provide controlled synthetic case access.
- **Pathway-rules tools and MCP server:** provide validated target configuration.
- **Policy-evidence tools and MCP server:** retrieve controlled local supporting evidence.
- **Reusable Agent Skills:** define portable skill metadata, schemas, examples and bounded local execution for pathway identification, risk calculation, evidence retrieval and escalation drafting.
- **Structured schemas:** define synthetic cases, assessments, recommendations, and review state.
- **Deterministic services:** implement Milestone 2 assessment and risk logic without LLM or external API calls.
- **ADK orchestration layer:** defines coordinator, pathway, risk, evidence, escalation and review agents with controlled local tools.
- **Guardrails:** protect against personal data, prompt injection, unsupported claims, unsafe output, and autonomous escalation.
- **Audit logging:** records inputs, tool calls, calculations, evidence metadata, validation, and human decisions.
- **Human approval:** required before finalising any escalation.
- **Evaluation framework:** measures correctness, grounding, safety, and reproducibility.
- **Deployment boundary:** future Cloud Run service boundary with externalised secrets and least-privilege configuration.

## Planned Flow

1. A reviewer submits a synthetic case.
2. Guardrails validate the input and reject unsafe or identifiable content.
3. The ADK orchestration layer coordinates specialist agents around deterministic tools in Milestone 3.
4. Tools or MCP-compatible servers provide controlled case data, pathway targets and evidence.
5. Structured schemas validate each output.
6. Audit logging records the execution trace.
7. The review agent routes the draft to a human reviewer.
8. Human approval is required before finalisation.

## Design Principles

- Synthetic data only.
- Deterministic calculations for target and breach status.
- Explicit separation between retrieved evidence and inference.
- Schema-first outputs.
- Fail-safe behavior.
- No clinical decision authority.
- Reproducible local development.

See [architecture.mmd](diagrams/architecture.mmd) for the Mermaid diagram.
