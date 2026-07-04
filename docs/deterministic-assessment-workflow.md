# Deterministic Assessment Workflow

Milestone 2 assessment is local, deterministic and independent of LLMs or external APIs.

## Workflow

1. Load a synthetic case from `data/synthetic_cases.json`.
2. Reject cases that are not synthetic, contain prohibited identity fields, have malformed timestamps, use unsupported pathway codes, or have assessment time before referral or arrival time.
3. Load the applicable demonstration pathway rule from `data/pathway_targets.json`.
4. Calculate elapsed time from `referral_or_arrival_datetime` to `assessment_datetime`.
5. Convert elapsed time into the rule target unit, supporting hours and days.
6. Round elapsed values and percentages to two decimal places using deterministic decimal rounding.
7. Calculate target consumption, variance from target and breach status.
8. Evaluate operational risk factors and clamp the score to 0 to 10.
9. Generate deterministic non-clinical recommended actions.
10. Record assumptions, warnings and an audit trace.
11. Return a validated assessment or escalation draft with human review pending.

## Timezone Handling

Datetimes must be timezone-aware. Naive datetimes are rejected to avoid ambiguous elapsed-time calculations.

## Audit Trace

Each assessment contains a unique trace ID, timestamps, rule version, rule used, calculation steps, risk factors applied, warnings, human review requirement and outcome status. Audit traces must not contain secrets or real patient-identifiable information.

## Milestone Boundaries

This deterministic workflow remains available independently of Google ADK. Milestone 3 wraps it in ADK agent orchestration for mock and live-configured execution, but deterministic values remain authoritative.
