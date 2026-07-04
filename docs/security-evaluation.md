# Security Evaluation

The deterministic security evaluator uses `evaluation/security_cases.json`.

It includes 30 synthetic cases covering safe input, prompt injection, deterministic override attempts, review bypass, clinical advice, autonomous-action claims, tool misuse, path traversal, oversized input, secrets, personal data, malicious evidence, malformed output, immutable amendments and unsupported claims.

Run:

```bash
python3 -m app.main run-security-evaluation --json
```

The evaluator does not call Gemini and does not use network access. It reports pass rate, false positives and false negatives.
