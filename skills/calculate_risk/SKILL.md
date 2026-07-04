# Calculate Risk Skill

## Purpose

Calculate deterministic, explainable operational risk for a synthetic pathway case.

## When To Use

Use to run the deterministic assessment and return exact risk score, level and factors.

## When Not To Use

Do not use to create alternative model-based scores or clinical prioritisation.

## Inputs

Validated synthetic case ID.

## Outputs

Breach status, target consumption, variance, risk score, risk level, risk factors, audit trace ID and human-review requirement.

## Dependencies

Pathway Rules MCP server and deterministic assessment service.

## Deterministic vs Model Components

All calculations are deterministic. Models may only explain supplied factors.

## Failure Conditions

Unknown case, unsupported pathway, malformed timestamps, unavailable MCP capability.

## Example Invocation

`python -m app.main run-skill --skill calculate_risk --case-id SYN-CANCER-2WW-001`

## Evaluation Criteria

Exact deterministic risk values preserved and every factor explained.

## Current Limitations

Operational risk only; no clinical logic.

## Safety Requirements

- Use transparent factors.
- Keep calculations reproducible.
- Do not infer clinical diagnosis or treatment needs.
- Require human review for downstream outputs.
