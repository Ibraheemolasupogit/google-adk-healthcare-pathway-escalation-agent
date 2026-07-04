# Generate Escalation Skill

## Purpose

Generate a structured operational escalation draft from validated pathway assessment and evidence.

## When To Use

Use to generate a structured operational escalation draft from validated case, assessment, evidence and action inputs.

## When Not To Use

Do not use to submit escalation, provide clinical advice, or override deterministic values.

## Inputs

Synthetic case, deterministic assessment, retrieved evidence and recommended actions.

## Outputs

Structured draft sections, assumptions, warnings, review status and `human_review_required=true`.

## Dependencies

Case Data, Pathway Rules and Policy Evidence MCP servers plus deterministic assessment services.

## Deterministic vs Model Components

Numerical and status values are deterministic. Narrative organisation may be model-generated but must preserve values.

## Failure Conditions

Invalid assessment, unsupported evidence, prohibited clinical language, failed review validation.

## Example Invocation

`python -m app.main run-skill --skill generate_escalation --case-id SYN-CANCER-2WW-001`

## Evaluation Criteria

Required sections present, no submission claim, human review pending, deterministic values preserved.

## Current Limitations

No human approval UI and no autonomous submission.

## Safety Requirements

- Do not autonomously send or finalise escalation.
- Avoid clinical diagnosis or treatment recommendations.
- Include unsupported-claim checks.
- Require human approval before finalisation.
