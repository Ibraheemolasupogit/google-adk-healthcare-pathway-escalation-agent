# Development Assistants And Runtime Technologies

This page separates development workflow from runtime architecture. Development assistants helped with implementation, review and documentation. They are not runtime dependencies and do not own the architecture.

## Antigravity

Antigravity is treated here as a course development environment or assistant context. The repository does not contain tracked Antigravity screenshots, session exports or implementation logs. Therefore the project does not claim that Antigravity built the application, is required at runtime, or is needed for deployment.

Where Antigravity is mentioned, it is limited to development-process context and course learning context. See [Antigravity evidence](evidence/antigravity/README.md) for the current evidence status and checklist for adding future genuine evidence.

## Codex

Codex-assisted development is evidenced by the repository workflow in this environment and by changes produced through milestone implementation, documentation, validation and defect correction. Codex supported repository scaffolding, milestone implementation, test generation, documentation drafting, final submission checks and the Streamlit import-shadowing correction.

Codex was not the source of architectural authority. Human requirements set the problem, safety boundaries, milestone acceptance criteria and final acceptance decisions.

## Human Role

The project owner retained responsibility for:

- Problem selection and scope.
- Architecture and runtime boundaries.
- Synthetic-data and responsible-AI constraints.
- Review of generated changes.
- Acceptance or rejection of implementation suggestions.
- Kaggle submission ownership.

## Runtime Technologies

The runtime implementation uses:

- Python for services, CLI, tests and scripts.
- Google ADK for agent definitions and orchestration structure.
- MCP-compatible local adapters for case, pathway and evidence capabilities.
- Pydantic for schemas and structured validation.
- Streamlit for the public demonstration interface.
- Deterministic services for pathway status, risk scoring and review invariants.

These runtime components are independent of Antigravity and Codex.

## Development Workflow

The development workflow combines natural-language specifications, milestone tasks, generated drafts, human review and automated gates. The gates include Ruff, mypy, pytest, security evaluation, benchmark evaluation, deployment verification and final submission validation.

## Boundary Statement

Development assistants can accelerate implementation and documentation. They do not remove the need for domain review, tests, safety checks, benchmark validation or clear claims about what the system does and does not do.
