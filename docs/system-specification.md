# System Specification

## Project Scope

The project provides a deterministic Milestone 2 domain layer for analysing synthetic NHS operational pathway cases, calculating pathway status, generating operational risk scores, drafting non-clinical escalation recommendations, and requiring human approval before finalisation. Future milestones will add agent orchestration and evidence retrieval.

## Goals

- Demonstrate a responsible multi-agent architecture for the Kaggle Agents for Good track.
- Use synthetic data only.
- Keep pathway target and breach calculations deterministic and auditable.
- Separate retrieved evidence from model inference.
- Require human review for every escalation output.

## Non-Goals

- No clinical diagnosis, triage, treatment, or autonomous clinical decision-making.
- No use of real patient-identifiable data.
- No production NHS deployment in Milestone 2.
- No Gemini, Google ADK orchestration, MCP network service, or frontend implementation in Milestone 2.

## Functional Requirements

- **FR-01:** Accept a synthetic NHS pathway case.
- **FR-02:** Determine the applicable pathway target.
- **FR-03:** Calculate target and breach status deterministically.
- **FR-04:** Calculate an explainable operational risk score.
- **FR-05:** Retrieve supporting pathway evidence in a future milestone.
- **FR-06:** Generate recommended operational actions.
- **FR-07:** Require human approval before finalising an escalation.
- **FR-08:** Record an auditable execution trace.

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

- Milestone 2 is deterministic local domain logic only.
- Secrets must not be committed.
- Functional AI-agent behavior is deferred.
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
5. Evidence retrieval remains planned for a later milestone.
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

## Auditability Requirements

- Record pathway target source metadata.
- Record deterministic calculation inputs and outputs.
- Record evidence retrieval source metadata in a future milestone.
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

- Repository structure supports the Milestone 2 deterministic domain layer.
- Placeholder agent and MCP modules remain non-network and non-LLM.
- Schemas validate synthetic cases, rules, assessments, escalation drafts and audit traces.
- Documentation clearly separates implemented deterministic functionality from planned AI-agent functionality.
- Quality checks pass.

## Definition of Done

Milestone 2 is done when deterministic rules, case validation, breach assessment, risk scoring, recommended actions, audit traces, CLI commands, documentation and tests are present and passing, with no real patient data, no secrets, no deployment, and no production AI-agent behavior.
