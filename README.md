# NHS Pathway Escalation and Evidence Agent

NHS Pathway Escalation and Evidence Agent is a portfolio-quality Google AI agent project foundation for analysing synthetic NHS operational pathway cases, identifying target and breach status, retrieving controlled supporting evidence, drafting escalation recommendations, and requiring human approval before any final output.

This repository is being prepared for the Kaggle competition **AI Agents: Intensive Vibe Coding Capstone Project** under the **Agents for Good** track. It currently contains the **Milestone 1 foundation only**: documentation, repository structure, schemas, placeholder modules, synthetic demonstration data, development configuration, and validation tests. Functional agent execution will follow in later milestones.

## Problem Statement

Operational pathway teams need timely, auditable support when synthetic cases approach or breach pathway targets. Future versions of this project will explore how agentic workflows can help organise operational evidence and draft escalation recommendations without making clinical decisions.

## Proposed Solution

The planned system will coordinate specialist agents that classify the pathway, calculate deterministic target status, estimate explainable operational risk, retrieve supporting evidence, draft escalation actions, validate outputs, and route all recommendations through human review.

## Intended Users

- NHS operational pathway coordinators working with synthetic or training data.
- Service managers reviewing pathway risk and escalation drafts.
- Kaggle evaluators assessing agent architecture and responsible-AI design.
- Developers extending the project in later milestones.

## Key Capabilities

- Accept synthetic NHS pathway cases.
- Determine the applicable operational pathway target.
- Calculate target status and breach status deterministically.
- Calculate an explainable operational risk score.
- Retrieve controlled supporting evidence.
- Generate structured escalation drafts.
- Require human approval before finalisation.
- Record auditable execution traces.

## Planned Multi-Agent Architecture

The future workflow will use a coordinator agent that delegates to pathway, risk, evidence, escalation, and review agents. The review agent will enforce schema validation, safety requirements, evidence grounding, and human approval before a final escalation can be completed.

## Planned Google Technologies

- Google Agent Development Kit for agent orchestration.
- Gemini for future language-model reasoning and drafting.
- Antigravity for project development support.
- MCP-compatible tools or servers for controlled case, pathway, and evidence access.
- Agent Skills for reusable agent task instructions.
- Google Cloud Run for future deployment.

## Planned Agent Responsibilities

- **Coordinator Agent:** controls workflow, delegates tasks, assembles the final draft, and ensures review steps occur.
- **Pathway Agent:** identifies pathway type, obtains the applicable target, and does not invent targets.
- **Risk Agent:** performs deterministic calculations, calculates explainable risk, and returns contributing factors.
- **Evidence Agent:** retrieves controlled evidence, distinguishes retrieved evidence from model inference, and provides source metadata.
- **Escalation Agent:** generates a structured draft and does not autonomously send or finalise escalation.
- **Review Agent:** validates completeness, checks unsupported claims, enforces schema and safety requirements, and routes output for human approval.

## Security and Responsible AI

This project is designed around synthetic data, least-privilege tools, schema validation, auditable tool activity, prompt-injection resistance, controlled evidence retrieval, fail-safe behavior, and explicit human-in-the-loop approval. It must never claim clinical diagnosis, treatment recommendation, or autonomous clinical decision-making authority.

## Human in the Loop

All escalation outputs must include `human_review_required`. Future versions will require a human reviewer to inspect evidence, risks, and recommendations before any final escalation is approved.

## Synthetic Data Limitation

Only synthetic demonstration data is included. Do not add real names, NHS numbers, addresses, dates of birth, hospital numbers, or identifiable clinical details. Demonstration pathway targets are illustrative only and must be validated against current authoritative guidance before any operational use.

## Repository Structure

```text
.
├── app/                 # Placeholder CLI and configuration
├── agents/              # Planned agent boundaries
├── skills/              # Agent Skill specifications
├── tools/               # Planned local tool interfaces
├── mcp_servers/         # Planned MCP-compatible server placeholders
├── data/                # Synthetic sample data only
├── schemas/             # Pydantic schemas
├── evaluation/          # Future evaluation fixtures and evaluator placeholder
├── security/            # Guardrails, validation, and threat model
├── tests/               # Unit, integration, and security tests
├── docs/                # Architecture, specification, roadmap, and submission docs
├── deployment/          # Future deployment placeholder
└── scripts/             # Project validation script
```

## Local Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
make install
```

Copy `.env.example` to `.env` only for local development in later milestones, and never commit secrets.

## Development Commands

```bash
make format
make lint
make type-check
make test
make quality
make run
make validate-project
```

## Planned Evaluation Approach

Future evaluation will measure pathway-target retrieval accuracy, breach-calculation accuracy, risk-classification accuracy, schema compliance, evidence grounding, tool-selection accuracy, unsupported-claim rate, human-review enforcement, prompt-injection resistance, and reproducibility.

## Roadmap

- **Milestone 1:** Repository foundation, architecture, and specification.
- **Milestone 2:** Deterministic pathway models, schemas, and synthetic data.
- **Milestone 3:** Google ADK agent orchestration.
- **Milestone 4:** Tools, MCP interoperability, and Agent Skills.
- **Milestone 5:** Security guardrails and human-in-the-loop workflow.
- **Milestone 6:** Evaluation dataset and automated evaluation.
- **Milestone 7:** User interface and Cloud Run deployment.
- **Milestone 8:** Kaggle write-up, video, and final submission assets.

## Current Milestone Status

Milestone 1 is installed. Functional AI agent execution, Gemini calls, Google ADK orchestration, MCP network services, deployment, and production workflows are not implemented yet.

## Disclaimer

This repository is for education, competition demonstration, and software architecture development using synthetic data only. It does not provide medical advice, clinical diagnosis, treatment recommendations, operational policy authority, or autonomous clinical decision-making.

## Licence

This project is released under the MIT License. See [LICENSE](LICENSE).
