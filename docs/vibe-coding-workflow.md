# Spec-Driven Vibe Coding Workflow

This project uses vibe coding as a development method: natural-language intent is turned into milestone specifications, implementation tasks, review checks and validation gates. The method is not a runtime feature. The runtime system is still ordinary Python software built from deterministic services, Google ADK agent definitions, local MCP-compatible adapters, Agent Skills, Pydantic schemas and Streamlit.

## Initial Problem Specification

The starting problem was to demonstrate a responsible agent system for synthetic NHS operational pathway review. The system needed to identify pathway status, preserve deterministic calculations, retrieve controlled evidence, draft non-clinical operational escalation text and require human review before any finalisation. The current [system specification](system-specification.md) records the accepted scope, goals, non-goals, safety boundaries and acceptance criteria.

## Milestone Sequence

The repository history and [roadmap](roadmap.md) show a milestone-based flow:

1. Repository foundation, specification and architecture.
2. Deterministic domain engine for synthetic pathway assessment.
3. Google ADK orchestration around deterministic services.
4. MCP interoperability and reusable Agent Skills.
5. Guardrails and backend human review.
6. Evaluation framework and reproducibility evidence.
7. Streamlit interface and deployment readiness.
8. Final Kaggle submission package.
9. Streamlit import-shadowing defect correction by renaming `ui/services.py` to `ui/demo_service.py`.

## Specification Before Implementation

Each milestone narrowed a natural-language request into concrete files, commands and acceptance checks. The project specification defines what the system must do and, just as importantly, what it must not do: no real patient data, no clinical advice, no autonomous escalation, no live NHS integration and no production deployment claim.

## Generated-Code Review Process

Development assistants were used to help draft code, tests and documentation. Generated changes were not treated as automatically correct. Changes were reviewed against the specification, repository conventions and safety constraints, then accepted only after automated validation. The project owner retained responsibility for requirements, architecture, safety boundaries and acceptance decisions.

## Human Architectural Control

The architecture keeps deterministic calculations authoritative. Agent-generated narrative may explain or draft around those values, but it must not replace pathway status, risk score, breach status or review state. This boundary is a human design decision reflected in schemas, services, tests and documentation.

## Quality Gates

Quality gates include Ruff linting, Ruff formatting checks, mypy type checking, unit tests, integration tests, deployment verification and final submission validation. The command set is documented in the README and exercised by `scripts/validate_project.py`, `scripts/verify_deployment.py` and `scripts/final_submission_check.py`.

## Security Gates

Security gates include synthetic-data constraints, secret redaction, prompt-injection checks, deterministic-override detection, path-traversal checks, personal-data pattern checks, review-bypass detection and no tracked runtime artifacts. Security behavior is covered by `tests/security/`, `services/guardrail_service.py`, `services/security_evaluator.py` and `evaluation/security_cases.json`.

## Evaluation Gates

Evaluation gates use a controlled 30-case synthetic benchmark and committed evidence under `docs/evidence/milestone-6/`. The framework checks deterministic exact matches, mock and mock-MCP agent preservation, skill behavior, evidence grounding, review-state controls, security and reproducibility. These are controlled benchmark results, not production claims.

## Defects Identified And Corrected

- A Streamlit import-shadowing defect was fixed after `ui/services.py` conflicted with the top-level `services/` package when Streamlit placed `ui/` early on `sys.path`. The permanent correction renamed the UI helper module to `ui/demo_service.py` and updated imports.
- Submission readiness checks were added to catch unsafe public documentation patterns such as local absolute paths, credential-like strings, unsupported deployment claims and fake public URLs.
- Linting identified import-order issues during the UI service rename. The imports were sorted and the checks rerun.

## Suggestions Versus Accepted Implementation

Assistant-generated suggestions were treated as drafts. Accepted implementation had to fit the repository structure, maintain deterministic authority, preserve benchmark expectations and pass the validation gates. Suggestions that would imply live NHS connectivity, production safety, autonomous clinical action or unverified live model behavior are outside the accepted scope.

## Lessons Learned

- Vibe coding works best when paired with explicit acceptance criteria.
- Deterministic service boundaries reduce ambiguity in safety-sensitive demonstrations.
- Documentation needs the same review discipline as code because public claims can overstate capability.
- Runtime naming matters: a small module name such as `services.py` can shadow an important package in framework-specific execution contexts.

## Limitations

The workflow documentation is based on tracked repository files, commit history and validation artifacts. It does not include private chat transcripts, untracked screenshots or external development-session records. Antigravity usage is not claimed as an implementation dependency unless supported by evidence in [Antigravity evidence](evidence/antigravity/README.md).

## Relationship To The Kaggle Course

The Kaggle capstone rewards building useful agent systems through rapid, specification-led iteration. This project uses vibe coding for that development workflow while keeping the user-facing value proposition focused on responsible agent architecture: deterministic assessment, ADK orchestration, MCP interoperability, Agent Skills, guardrails, evaluation and human review.
