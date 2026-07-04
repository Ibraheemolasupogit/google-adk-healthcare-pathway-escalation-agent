# Identify Pathway Skill

## Purpose

Identify the pathway category for a synthetic operational case and retrieve the applicable target from controlled configuration.

## When To Use

Use when a synthetic case must be validated and mapped to a controlled demonstration pathway rule.

## When Not To Use

Do not use for unsupported pathways, real patient data, or target calculation from model knowledge.

## Inputs

`case_id` or a validated synthetic case.

## Outputs

Pathway code, pathway name, rule metadata, target, target unit, demonstration-only flag and validation warnings.

## Dependencies

Case Data MCP server and Pathway Rules MCP server.

## Deterministic vs Model Components

Case validation and rule lookup are deterministic. Any narrative explanation is model-generated and must not alter deterministic values.

## Failure Conditions

Unknown case, unsupported pathway, prohibited identity fields, unavailable MCP capability.

## Example Invocation

`python -m app.main run-skill --skill identify_pathway --case-id SYN-CANCER-2WW-001`

## Evaluation Criteria

Correct pathway code, controlled target metadata, warnings present and no invented target values.

## Current Limitations

Demonstration-only local data. Validate targets against authoritative guidance before operational use.

## Safety Requirements

- Use synthetic cases only.
- Do not invent pathway targets.
- Return uncertainty when a pathway cannot be mapped.
- Require human review for downstream outputs.
