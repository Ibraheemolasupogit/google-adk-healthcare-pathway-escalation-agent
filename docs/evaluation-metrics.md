# Evaluation Metrics

Milestone 6 metrics are controlled benchmark metrics for a synthetic dataset. They are not claims about clinical safety, production performance or live model reliability.

## Core Metrics

- `pathway_accuracy`: exact match between expected and actual pathway code.
- `breach_status_accuracy`: exact match for deterministic breach status.
- `risk_level_accuracy`: exact match for deterministic operational risk level.
- `risk_score_exact_match_rate`: exact match for deterministic risk score.
- `action_code_accuracy`: exact match for recommended deterministic action codes.
- `schema_compliance_rate`: all required structured fields are present and valid.
- `deterministic_preservation_rate`: agents and skills preserve deterministic assessment fields.
- `evidence_grounding_rate`: generated outputs cite expected local evidence IDs.
- `unsupported_claim_free_rate`: agent outputs avoid unsupported claims.
- `human_review_enforcement_rate`: outputs remain pending human review.
- `blocking_case_pass_rate`: expected guardrail blocking cases are blocked.
- `valid_transition_rate`: human-review state transitions follow the state machine.
- `integrity_detection_rate`: tampered review records are detected.
- `submitted_false_rate`: no automated evaluator marks an item submitted to an external system.
- `deterministic_reproducibility_rate`: deterministic outputs hash identically after volatile-field normalisation.

The full metric snapshot for the latest committed Milestone 6 run is in `docs/evidence/milestone-6/metric-summary.csv`.

