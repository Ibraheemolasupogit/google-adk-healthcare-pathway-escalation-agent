# Course Concept Mapping

## Vibe Coding

- Implemented evidence: milestone-driven repository history, natural-language specifications, acceptance criteria and final documentation in `docs/vibe-coding-workflow.md`.
- Principal files: `docs/system-specification.md`, `docs/roadmap.md`, `docs/vibe-coding-workflow.md`.
- Type: development process.
- Demonstration method: public docs explain how generated suggestions were reviewed against tests, security checks and benchmark gates.
- Limitations: vibe coding is not a runtime feature and does not replace human architectural responsibility.

## Spec-Driven Development

- Implemented evidence: explicit system scope, non-goals, requirements, safety constraints and definition-of-done language.
- Principal files: `docs/system-specification.md`, `README.md`, `scripts/validate_project.py`.
- Type: development process.
- Demonstration method: validation scripts check required project and submission files.
- Limitations: requirements are for this synthetic demonstration, not production NHS deployment.

## Antigravity

- Implemented evidence: no tracked implementation evidence was found, so the repository documents Antigravity conservatively as course/development context only.
- Principal files: `docs/development-assistants.md`, `docs/evidence/antigravity/README.md`.
- Type: development process only.
- Demonstration method: evidence page states current evidence status and checklist for future genuine evidence.
- Limitations: Antigravity is not a runtime dependency, deployment dependency or claimed implementation source.

## Codex

- Implemented evidence: Codex-assisted work supported repository scaffolding, milestone implementation, documentation, validation and defect correction in this development environment.
- Principal files: `docs/development-assistants.md`, validation scripts and tests.
- Type: development process.
- Demonstration method: documentation distinguishes assistant support from human approval and runtime architecture.
- Limitations: Codex is not a runtime component and does not own the architecture.

## Google ADK

- Implemented evidence: multi-agent orchestration with Coordinator, Pathway, Risk, Evidence, Escalation and Review agents.
- Principal files: `agents/`, `agents/registry.py`, `services/agent_orchestrator.py`, `schemas/agent.py`.
- Type: runtime.
- Demonstration method: CLI and Streamlit show structured agent steps in mock and mock-MCP modes.
- Limitations: live Gemini execution is configured as an optional path but was not verified.

## MCP

- Implemented evidence: local MCP-compatible servers, registry and bounded client for case, pathway and evidence capabilities.
- Principal files: `mcp_servers/`, `mcp_servers/client.py`, `docs/mcp-architecture.md`, `docs/mcp-tool-catalogue.md`.
- Type: runtime.
- Demonstration method: `mock-mcp` mode exercises local MCP-compatible calls.
- Limitations: no live NHS system integration and no public network MCP endpoint.

## Agent Skills

- Implemented evidence: approved local skills for `identify_pathway`, `calculate_risk`, `retrieve_evidence` and `generate_escalation`.
- Principal files: `skills/`, `services/skill_executor.py`, `tests/unit/test_skills.py`, `docs/skills-showcase.md`.
- Type: runtime.
- Demonstration method: CLI skill commands and skill evaluation check loading, input validation, output validation and deterministic preservation.
- Limitations: no arbitrary skill upload or untrusted skill execution.

## Security

- Implemented evidence: prompt-injection checks, deterministic-override checks, personal-data checks, secret redaction, evidence validation and review-bypass checks.
- Principal files: `services/guardrail_service.py`, `services/security_utils.py`, `services/security_evaluator.py`, `evaluation/security_cases.json`, `tests/security/`.
- Type: runtime and evaluation.
- Demonstration method: UI guardrail tab, CLI security commands and security evaluation.
- Limitations: deterministic guardrails are pragmatic controls, not complete protection.

## Human-In-The-Loop

- Implemented evidence: backend review workflow, review-state machine, immutable deterministic fields and tamper-evident hashes.
- Principal files: `services/human_review_service.py`, `schemas/review.py`, `ui/demo_service.py`, `docs/human-review-workflow.md`.
- Type: runtime.
- Demonstration method: Streamlit Human Review tab and CLI review commands require a reviewer alias before approve, amend or reject decisions.
- Limitations: reviewer alias is not authenticated identity and approval is demonstration-only.

## Evaluation

- Implemented evidence: 30-case synthetic benchmark and automated deterministic, mock, mock-MCP, skill, evidence, security, review and reproducibility evaluation.
- Principal files: `evaluation/`, `services/evaluation/`, `docs/evidence/milestone-6/`.
- Type: development workflow and evidence.
- Demonstration method: `python3 -m app.main run-full-evaluation` and Streamlit evaluation evidence tab.
- Limitations: results are controlled synthetic benchmark results, not production performance claims.

## Deployment Readiness

- Implemented evidence: Streamlit UI, Dockerfile, Cloud Run-ready documentation, service example and deployment verification script.
- Principal files: `ui/`, `deployment/`, `scripts/verify_deployment.py`, `docs/cloud-run-readiness.md`.
- Type: deployment readiness.
- Demonstration method: local Streamlit startup and deployment verification script.
- Limitations: Cloud Run deployment was not performed.
