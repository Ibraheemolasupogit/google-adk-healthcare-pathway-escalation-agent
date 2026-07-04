# System Specification

## Project Scope

The project will provide an agentic workflow for analysing synthetic NHS operational pathway cases, calculating pathway status, retrieving supporting evidence, drafting escalation recommendations, and requiring human approval before finalisation.

## Goals

- Demonstrate a responsible multi-agent architecture for the Kaggle Agents for Good track.
- Use synthetic data only.
- Keep pathway target and breach calculations deterministic and auditable.
- Separate retrieved evidence from model inference.
- Require human review for every escalation output.

## Non-Goals

- No clinical diagnosis, triage, treatment, or autonomous clinical decision-making.
- No use of real patient-identifiable data.
- No production NHS deployment in Milestone 1.
- No Gemini, Google ADK orchestration, MCP network service, or frontend implementation in Milestone 1.

## Functional Requirements

- **FR-01:** Accept a synthetic NHS pathway case.
- **FR-02:** Determine the applicable pathway target.
- **FR-03:** Calculate target and breach status deterministically.
- **FR-04:** Calculate an explainable operational risk score.
- **FR-05:** Retrieve supporting pathway evidence.
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

- Milestone 1 is documentation and scaffold only.
- Secrets must not be committed.
- Functional agent behavior is deferred.
- All outputs must include `human_review_required`.

## System Actors

- **Operational reviewer:** reviews draft escalation outputs.
- **Developer:** extends and tests the system.
- **Coordinator agent:** controls the planned workflow.
- **Specialist agents:** perform planned pathway, risk, evidence, escalation, and review tasks.
- **Evaluation framework:** measures correctness, safety, and reproducibility.

## Principal Workflows

1. Synthetic case is submitted.
2. Coordinator agent validates input shape and synthetic-data constraints.
3. Pathway agent identifies the pathway and controlled target.
4. Risk agent calculates breach status and operational risk.
5. Evidence agent retrieves supporting evidence with metadata.
6. Escalation agent drafts recommended operational actions.
7. Review agent validates schema, evidence grounding, unsupported claims, and safety.
8. Human reviewer approves, rejects, or requests changes.
9. Audit trace records inputs, tool activity, validation results, and review outcome.

## Input Schema

The minimal synthetic case schema includes:

- `case_id`
- `synthetic`
- `pathway_type`
- `referral_or_arrival_day`
- `current_day`
- `status`
- `operational_context`
- `human_review_required`

## Output Schema

The minimal escalation recommendation schema includes:

- `case_id`
- `summary`
- `recommended_actions`
- `supporting_evidence`
- `unsupported_claims`
- `human_review_required`
- `approved_by_human`

## Human-Review Requirements

- Every output must require human review.
- Escalations must not be sent automatically.
- Review status must be recorded.
- Unsupported claims must be surfaced to the reviewer.

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

- Repository structure matches the Milestone 1 plan.
- Placeholder modules are importable and non-operational.
- Schemas validate minimal synthetic cases and escalation drafts.
- Documentation clearly separates planned functionality from implemented foundation.
- Quality checks pass.

## Definition of Done

Milestone 1 is done when the scaffold, documentation, schemas, synthetic sample data, tests, validation script, and development commands are present and passing, with no real patient data, no secrets, no deployment, and no production agent behavior.
