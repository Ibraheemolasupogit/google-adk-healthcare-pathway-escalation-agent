# Guardrail Architecture

Milestone 5 adds `services/guardrail_service.py` as the central deterministic guardrail pipeline.

The pipeline checks:

- user input and case payloads;
- local evidence records;
- deterministic value integrity;
- prohibited clinical or autonomous-action language;
- unsupported claims;
- malformed output;
- review-state invariants;
- prompt-injection and tool-misuse attempts.

Severities are `INFO`, `WARNING` and `BLOCKING`. A `BLOCKING` finding prevents a draft from being treated as safe for human review.

The checks are pragmatic deterministic rules, not a complete prompt-injection or personal-data detection system.
