# Skills Showcase

This page summarises the capabilities demonstrated by the project and separates runtime behavior, development workflow and deployment readiness.

## Agent Engineering

### Google ADK Multi-Agent Orchestration

- Demonstrates: coordinator and specialist agents for pathway, risk, evidence, escalation and review steps.
- Principal files: `agents/`, `agents/registry.py`, `services/agent_orchestrator.py`, `schemas/agent.py`.
- Category: runtime.
- Limitations: public demo uses mock and mock-MCP modes; live Gemini execution was not verified.

### Tool Boundaries And Structured Outputs

- Demonstrates: agents call controlled tools and return schema-validated records.
- Principal files: `tools/adk_tools.py`, `schemas/agent.py`, `services/agent_review.py`.
- Category: runtime.
- Limitations: tool access is local and demonstration-only.

## Interoperability

### MCP Servers, Registry And Client

- Demonstrates: local MCP-compatible case, pathway and evidence capabilities with a bounded client.
- Principal files: `mcp_servers/`, `mcp_servers/registry.py`, `mcp_servers/client.py`.
- Category: runtime.
- Limitations: no live NHS integration and no public network MCP endpoint.

### Tool Allow-Listing And Local Evidence Retrieval

- Demonstrates: constrained capabilities and controlled evidence access.
- Principal files: `tools/evidence_tools.py`, `data/evidence/local_evidence.json`, `services/guardrail_service.py`.
- Category: runtime.
- Limitations: evidence is synthetic demonstration evidence and requires external validation before operational use.

## Reusable Agent Capabilities

### `identify_pathway`

- Demonstrates: pathway identification and rule lookup for a synthetic case.
- Principal files: `skills/identify_pathway/`, `services/skill_executor.py`.
- Category: runtime.
- Limitations: approved local skill only; no arbitrary skill upload.

### `calculate_risk`

- Demonstrates: deterministic risk values surfaced through a reusable skill.
- Principal files: `skills/calculate_risk/`, `services/risk_engine.py`, `services/assessment_service.py`.
- Category: runtime.
- Limitations: operational risk only; not clinical triage.

### `retrieve_evidence`

- Demonstrates: controlled local evidence retrieval through MCP-backed capabilities.
- Principal files: `skills/retrieve_evidence/`, `tools/evidence_tools.py`.
- Category: runtime.
- Limitations: local evidence is not current authoritative NHS guidance.

### `generate_escalation`

- Demonstrates: structured non-clinical draft generation requiring human review.
- Principal files: `skills/generate_escalation/`, `services/agent_orchestrator.py`, `services/human_review_service.py`.
- Category: runtime.
- Limitations: cannot approve or submit an escalation.

## Software Engineering

- Demonstrates: specification-driven development, Pydantic schemas, modular services, CLI commands, tests, typing, linting and containerisation.
- Principal files: `docs/system-specification.md`, `schemas/`, `services/`, `app/main.py`, `tests/`, `pyproject.toml`, `deployment/Dockerfile`.
- Category: development workflow and runtime.
- Limitations: container configuration is readiness evidence; Cloud Run deployment was not performed.

## Responsible AI And Security

- Demonstrates: synthetic data only, deterministic source of truth, prompt-injection controls, evidence validation, secret redaction, personal-data checks, least privilege, human review and immutable deterministic fields.
- Principal files: `services/guardrail_service.py`, `services/security_utils.py`, `services/human_review_service.py`, `evaluation/security_cases.json`, `tests/security/`.
- Category: runtime.
- Limitations: deterministic guardrails are pragmatic controls, not complete protection.

## Evaluation

- Demonstrates: 30-case synthetic benchmark, deterministic evaluation, mock and mock-MCP evaluation, security evaluation, review-state evaluation and reproducibility evaluation.
- Principal files: `evaluation/`, `services/evaluation/`, `docs/evidence/milestone-6/`.
- Category: development workflow and evidence.
- Limitations: controlled synthetic results are not production performance claims.

## Product And Deployment

- Demonstrates: Streamlit demo, presentation mode, Docker configuration, Cloud Run readiness and public documentation.
- Principal files: `ui/`, `deployment/`, `docs/user-interface.md`, `docs/cloud-run-readiness.md`, `submission/`.
- Category: runtime and deployment readiness.
- Limitations: final Kaggle submission, YouTube upload and Cloud Run deployment remain manual actions.
