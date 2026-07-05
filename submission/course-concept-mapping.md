# Course Concept Mapping

## Agent or Multi-Agent System with Google ADK

- Where implemented: `agents/`, `services/agent_orchestrator.py`.
- Key files: `agents/registry.py`, `agents/coordinator.py`, `services/agent_orchestrator.py`, `schemas/agent.py`.
- Demonstration: Streamlit and CLI show Coordinator, Pathway, Risk, Evidence, Escalation and Review agents.
- Limitations: Public demo uses mock and mock-MCP modes. Live Gemini execution was not verified.

## MCP Server Interoperability

- Where implemented: `mcp_servers/`, `mcp_servers/client.py`.
- Key files: `mcp_servers/case_data_server.py`, `mcp_servers/pathway_rules_server.py`, `mcp_servers/policy_evidence_server.py`.
- Demonstration: `mock-mcp` mode exercises local MCP-compatible case, rule and evidence capabilities.
- Limitations: No live NHS system integration and no public network MCP endpoint.

## Antigravity-Supported Development

- Where implemented: Development process and course workflow only.
- Key files: Not a runtime integration.
- Demonstration: The repository does not claim Antigravity runtime functionality.
- Limitations: Antigravity is not part of the deployed application or execution path.

## Agent Skills

- Where implemented: `services/skill_executor.py` and skill metadata under `skills/` where present.
- Key files: `services/skill_executor.py`, `schemas/mcp.py`, `tests/unit/test_skills.py`.
- Demonstration: Skills for pathway identification, risk calculation, evidence retrieval and escalation drafting are evaluated.
- Limitations: The public UI does not allow arbitrary skill upload or untrusted skill execution.

## Security Features

- Where implemented: `services/guardrail_service.py`, `services/security_utils.py`, `services/security_evaluator.py`.
- Key files: `evaluation/security_cases.json`, `tests/security/test_guardrails.py`, `docs/ui-security.md`.
- Demonstration: UI and CLI show guardrail status, findings and security evaluation results.
- Limitations: Deterministic guardrails are pragmatic checks, not complete protection.

## Human-in-the-Loop

- Where implemented: `services/human_review_service.py`, `schemas/review.py`, Streamlit Human Review tab.
- Key files: `services/human_review_service.py`, `tests/unit/test_human_review_service.py`, `ui/services.py`.
- Demonstration: Reviewer alias is required before approve, amend or reject decisions.
- Limitations: Reviewer alias is not authenticated identity.

## Evaluation

- Where implemented: `services/evaluation/`, `evaluation/`, `docs/evidence/milestone-6/`.
- Key files: `evaluation/benchmark_cases.json`, `services/evaluation/runner.py`, `docs/evidence/milestone-6/metric-summary.csv`.
- Demonstration: Full evaluation and UI evidence tab show controlled synthetic benchmark results.
- Limitations: Results are controlled synthetic benchmark results, not production performance.

## Deployment Readiness

- Where implemented: `deployment/`, `scripts/verify_deployment.py`, `ui/`.
- Key files: `deployment/Dockerfile`, `deployment/cloud-run.md`, `deployment/service.yaml.example`.
- Demonstration: Verification script checks imports, mock-MCP, evidence and container configuration.
- Limitations: Cloud Run deployment was not performed.

