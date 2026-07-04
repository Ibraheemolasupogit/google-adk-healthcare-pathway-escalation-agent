# System Specification

## Project Scope

The project provides deterministic pathway assessment, Google ADK mock orchestration, local MCP interoperability, security guardrails and backend human review for analysing synthetic NHS operational pathway cases, calculating pathway status, generating operational risk scores, drafting non-clinical escalation recommendations and requiring human approval before finalisation.

## Goals

- Demonstrate a responsible multi-agent architecture for the Kaggle Agents for Good track.
- Use synthetic data only.
- Keep pathway target and breach calculations deterministic and auditable.
- Separate retrieved evidence from model inference.
- Require human review for every escalation output.

## Non-Goals

- No clinical diagnosis, triage, treatment, or autonomous clinical decision-making.
- No use of real patient-identifiable data.
- No production NHS deployment.
- No frontend, Cloud Run deployment or autonomous escalation in Milestone 4.

## Functional Requirements

- **FR-01:** Accept a synthetic NHS pathway case.
- **FR-02:** Determine the applicable pathway target.
- **FR-03:** Calculate target and breach status deterministically.
- **FR-04:** Calculate an explainable operational risk score.
- **FR-05:** Retrieve supporting local demonstration pathway evidence through controlled tools or MCP-compatible adapters.
- **FR-06:** Generate recommended operational actions.
- **FR-07:** Require human approval before finalising an escalation.
- **FR-08:** Record an auditable execution trace.
- **FR-09:** Detect prompt injection, deterministic overrides, unsafe language, personal-data patterns and review-bypass attempts.
- **FR-10:** Record explicit backend human-review decisions without claiming authentication or submission.

## Non-Functional Requirements

- **NFR-01:** No real patient-identifiable data.
- **NFR-02:** Structured outputs must be schema validated.
- **NFR-03:** Secrets must be externally configured.
- **NFR-04:** Tool activity must be auditable.
- **NFR-05:** The system must fail safely.
- **NFR-06:** The system must not claim clinical decision authority.
- **NFR-07:** The project must be reproducible from documented instructions.

## Assumptions

- Inputs are synthetic and marked as synthetic.
- Authoritative pathway targets will be validated before any operational use.
- Human reviewers remain accountable for final decisions.
- Future Gemini outputs will be constrained by schemas, guardrails, and review checks.

## Constraints

- Milestone 4 adds local MCP-compatible server adapters and reusable Agent Skills while preserving deterministic values as the source of truth.
- Milestone 5 adds deterministic guardrails, tamper-evident review hashes and backend approve/amend/reject workflow.
- Secrets must not be committed.
- Live Gemini execution requires explicit Google configuration and is not required for tests.
- All outputs must include `human_review_required`.

## System Actors

- **Operational reviewer:** reviews draft escalation outputs.
- **Developer:** extends and tests the system.
- **Coordinator agent:** controls the planned workflow.
- **Specialist agents:** perform planned pathway, risk, evidence, escalation, and review tasks.
- **Evaluation framework:** measures correctness, safety, and reproducibility.

## Principal Workflows

1. Synthetic case is submitted.
2. Deterministic case tools validate input shape and synthetic-data constraints.
3. Pathway tools identify the controlled demonstration target rule.
4. The assessment service calculates breach status and operational risk.
5. Evidence retrieval returns controlled local demonstration evidence and remains validation-required.
6. The assessment service drafts recommended non-clinical operational actions.
7. Schemas validate completeness, review state and safety flags.
8. Human reviewer approves, rejects, or requests changes.
9. Audit trace records inputs, tool activity, validation results, and review outcome.

## Input Schema

The synthetic case schema includes:

- `case_id`
- `synthetic`
- `pathway_code`
- `referral_or_arrival_datetime`
- `assessment_datetime`
- `current_stage`
- `priority`
- `next_event_datetime`
- `operational_flags`
- `source_system`
- `notes`

## Output Schema

The final assessment and escalation schemas include:

- `case_id`
- `pathway_code`
- `pathway_name`
- `target`
- `elapsed_time`
- `breach_status`
- `variance_from_target`
- `risk_score`
- `risk_level`
- `risk_factors`
- `recommended_actions`
- `assumptions`
- `warnings`
- `demonstration_only`
- `human_review_required`
- `review_status`
- `audit_trace_id`

## Human-Review Requirements

- Every output must require human review.
- Escalations must not be sent automatically.
- Review status must be recorded.
- Unsupported claims must be surfaced to the reviewer.
- Human-review status `APPROVED_FOR_DEMONSTRATION` is not clinical, operational or submission approval.

## Auditability Requirements

- Record pathway target source metadata.
- Record deterministic calculation inputs and outputs.
- Record evidence retrieval source metadata.
- Record validation results and human approval state.
- Avoid logging secrets or patient-identifiable information.

## Security Requirements

- Reject real patient-identifiable data.
- Treat retrieved content as untrusted.
- Guard against prompt injection.
- Use least-privilege tools.
- Keep secrets outside source control.
- Fail closed when validation or evidence checks fail.

## Acceptance Criteria

- Repository structure supports the deterministic domain layer, ADK mock layer and local MCP layer.
- MCP servers are local, allow-listed and non-network for tests.
- Reusable Agent Skills include metadata, input schemas, output schemas and examples.
- Schemas validate synthetic cases, rules, assessments, escalation drafts, MCP invocations, skills and audit traces.
- Documentation clearly separates implemented local functionality from planned live model, UI and deployment functionality.
- Quality checks pass.

## Definition of Done

Milestone 4 is done when deterministic rules, ADK mock orchestration, local MCP adapters, reusable Agent Skills, CLI commands, documentation and tests are present and passing, with no real patient data, no secrets, no deployment and no autonomous escalation.
