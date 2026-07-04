# Agent Skills

Milestone 4 implements four approved local Agent Skills:

- `identify_pathway`
- `calculate_risk`
- `retrieve_evidence`
- `generate_escalation`

Each skill includes `SKILL.md`, metadata, JSON schemas and examples. Skills are loaded only from the static allow-list and executed through deterministic or MCP-backed capabilities.

Milestone 5 validates skill outputs with the central guardrail service. Skills remain demonstration-only, require human review, and cannot mark their own outputs as approved or submitted.

Milestone 6 adds `evaluate-skills`, which runs the approved skills over synthetic cases and checks skill loading, input validation, output validation and deterministic preservation.

Milestone 7 documents Agent Skills in the UI architecture section. The public UI does not allow arbitrary skill upload or execution.
