# Security Evaluation

The deterministic security evaluator uses `evaluation/security_cases.json`.

It includes 30 synthetic cases covering safe input, prompt injection, deterministic override attempts, review bypass, clinical advice, autonomous-action claims, tool misuse, path traversal, oversized input, secrets, personal data, malicious evidence, malformed output, immutable amendments and unsupported claims.

Run:

```bash
python3 -m app.main run-security-evaluation --json
```

The evaluator does not call Gemini and does not use network access. It reports pass rate, false positives and false negatives.

Milestone 6 includes the same security evaluator in `run-full-evaluation` and records precision, recall, F1, blocking-case pass rate and category-level results in `docs/evidence/milestone-6/metric-summary.csv`.
