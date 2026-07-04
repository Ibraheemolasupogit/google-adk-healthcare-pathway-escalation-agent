# Data And Secret Handling

The project uses synthetic data only. Guardrails reject common prohibited identity fields and obvious personal-data patterns such as NHS-number-like values, date-of-birth fields, patient-name fields, hospital-number fields, telephone markers, personal emails and postcode-like identity strings.

Secret redaction is centralised in `services/security_utils.py` for API-key, bearer-token, credential and common secret patterns.

Generated review records and assessment artifacts live under `artifacts/`, which is ignored by Git. No credentials are required for tests.

These checks are pragmatic safeguards for the demonstration and are not exhaustive PII discovery or production secret-scanning systems.
