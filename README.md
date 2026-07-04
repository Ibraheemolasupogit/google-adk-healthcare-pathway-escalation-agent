# NHS Pathway Escalation and Evidence Agent

NHS Pathway Escalation and Evidence Agent is a portfolio-quality project for the Kaggle **AI Agents: Intensive Vibe Coding Capstone Project** under the **Agents for Good** track. It currently implements a deterministic domain layer for synthetic NHS operational pathway cases: case validation, demonstration pathway-rule loading, elapsed-time calculation, breach classification, explainable operational risk scoring, operational action generation, audit traces and a CLI.

This repository now includes Google ADK orchestration, local MCP-compatible servers, a bounded MCP adapter, reusable Agent Skills and offline mock/mock-mcp execution. A human approval interface, frontend, deployment and final Kaggle assets remain planned later milestones.

## Implemented in Milestone 2

- Deterministic synthetic case validation.
- Controlled local pathway-rule loading from `data/pathway_targets.json`.
- Timezone-aware elapsed-time calculation for hour and day targets.
- Breach classification using rule warning and critical thresholds.
- Explainable operational risk scoring from 0 to 10.
- Deterministic non-clinical recommended actions.
- Structured Pydantic schemas for cases, rules, assessments, recommendations and audit traces.
- Audit trace generation for deterministic assessments.
- CLI commands for listing, showing, validating and assessing cases.
- Tests for domain logic, CLI behavior, data validation, security constraints and schema outputs.
- Google ADK-based agent definitions.
- Specialist-agent orchestration around deterministic tools.
- Safe ADK tool wrappers.
- Local demonstration evidence retrieval.
- Mock execution mode.
- Live Gemini configuration path.
- Structured review and agent audit records.
- Local MCP servers and bounded MCP client adapter.
- MCP tools and resources for case data, pathway rules and evidence.
- Reusable Agent Skills with registry and executor.
- Mock MCP execution mode.

## Planned Later

- Live Gemini execution in configured environments.
- Human approval user interface.
- Google Cloud Run deployment.
- Kaggle submission assets, video and demo materials.

## Problem Statement

Operational pathway teams need auditable support for identifying synthetic pathway cases that are within target, approaching target, at target, breached or substantially breached. This project explores how deterministic foundations can later support responsible agent workflows without making clinical decisions.

## Supported Demonstration Pathways

- `CANCER_2WW`: Cancer Two Week Wait.
- `CANCER_FDS_28`: Cancer 28-Day Faster Diagnosis.
- `CANCER_62`: Cancer 62-Day.
- `RTT_18_WEEK`: Referral to Treatment 18-Week.
- `UEC_4_HOUR`: Urgent and Emergency Care 4-Hour.

All pathway targets are demonstration data only. Operational users must validate targets against current authoritative NHS guidance before use.

## Security and Responsible AI

The project uses synthetic data only and must never include patient names, NHS numbers, dates of birth, hospital numbers, addresses or real clinical notes. The risk score is operational rather than clinical and must not be used for diagnosis, treatment, clinical prioritisation or autonomous clinical decision-making. Every assessment and escalation draft requires human review.

## Local Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
make install
```

Do not commit `.env` files or credentials.

## CLI

```bash
python -m app.main list-cases
python -m app.main show-case --case-id SYN-CANCER-2WW-001
python -m app.main assess-case --case-id SYN-CANCER-2WW-001
python -m app.main assess-all
python -m app.main list-pathways
python -m app.main validate-data
python -m app.main describe-risk-model
python -m app.main agent-assess --case-id SYN-CANCER-2WW-001 --mode mock
python -m app.main describe-agents
python -m app.main validate-agent-config
python -m app.main list-evidence
python -m app.main list-mcp-servers
python -m app.main validate-mcp-config
python -m app.main mcp-get-case --case-id SYN-CANCER-2WW-001
python -m app.main mcp-assess-case --case-id SYN-CANCER-2WW-001
python -m app.main list-skills
python -m app.main run-skill --skill identify_pathway --case-id SYN-CANCER-2WW-001
python -m app.main agent-assess --case-id SYN-CANCER-2WW-001 --mode mock-mcp
```

Most commands support `--json`. Assessment commands can write ignored runtime artifacts under `artifacts/assessments/`.

## Development Commands

```bash
make format
make lint
make type-check
make test
make quality
make run
make validate-data
make assess-samples
make validate-project
```

## Repository Structure

```text
app/          deterministic CLI
agents/       future agent placeholders
data/         synthetic cases and demonstration pathway rules
docs/         architecture, workflow, risk and data documentation
schemas/      Pydantic domain schemas
services/     deterministic assessment and risk services
tools/        case and pathway data/calculation tools
tests/        unit, integration and security tests
```

## Documentation

- [System specification](docs/system-specification.md)
- [Architecture](docs/architecture.md)
- [Deterministic assessment workflow](docs/deterministic-assessment-workflow.md)
- [Risk scoring methodology](docs/risk-scoring-methodology.md)
- [Data dictionary](docs/data-dictionary.md)
- [ADK agent architecture](docs/adk-agent-architecture.md)
- [Agent execution modes](docs/agent-execution-modes.md)
- [Live model configuration](docs/live-model-configuration.md)
- [MCP architecture](docs/mcp-architecture.md)
- [MCP tool catalogue](docs/mcp-tool-catalogue.md)
- [Agent Skills](docs/agent-skills.md)
- [Tool access matrix](docs/tool-access-matrix.md)
- [Roadmap](docs/roadmap.md)

## Disclaimer

This repository is for education, competition demonstration and software architecture development using synthetic data only. It does not provide medical advice, clinical diagnosis, treatment recommendations, operational policy authority or autonomous clinical decision-making.

## Licence

This project is released under the MIT License. See [LICENSE](LICENSE).
