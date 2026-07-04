# Reproducibility Methodology

The reproducibility evaluator repeats deterministic, mock agent and mock-MCP agent runs over the benchmark dataset and compares normalised hashes.

Volatile values are removed or normalised before hashing:

- request IDs
- audit trace IDs
- trace IDs
- timestamps
- duration fields
- review IDs
- record hashes

The evaluator keeps deterministic clinical-adjacent fields intact, including pathway code, target, elapsed time, breach status, risk score, risk level, risk factors, recommended actions, evidence IDs and human-review status.

Run:

```bash
python3 -m app.main evaluate-reproducibility --json
```

The full evaluation command also records reproducibility results:

```bash
python3 -m app.main run-full-evaluation --json
```

