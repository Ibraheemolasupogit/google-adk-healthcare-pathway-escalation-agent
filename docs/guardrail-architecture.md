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

Milestone 6 includes guardrail results in the full evaluation report with precision, recall, F1, blocking-case pass rate and category-level results for the controlled synthetic security dataset.

Milestone 7 displays guardrail status in the UI and uses safe error messages, validated downloads, redaction and read-only deterministic fields.
