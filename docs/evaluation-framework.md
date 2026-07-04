# Evaluation Framework

Milestone 6 adds an offline evaluation framework for deterministic assessment, mock agent behavior, mock-MCP agent behavior, Agent Skills, evidence grounding, guardrails, human review controls and reproducibility.

The framework is implemented in `services/evaluation/` and uses only synthetic local data. It does not call Gemini, NHS services or the network.

## Datasets

- `evaluation/benchmark_cases.json`: 30 synthetic benchmark cases, six per supported pathway.
- `evaluation/expected_assessments.json`: exact deterministic expected outputs.
- `evaluation/expected_agent_outputs.json`: expected mock and mock-MCP agent invariants.
- `evaluation/expected_skill_outputs.json`: expected Agent Skill invariants.
- `evaluation/evidence_grounding_cases.json`: evidence source and metadata checks.
- `evaluation/security_cases.json`: deterministic guardrail attack and safe-input cases.
- `evaluation/review_cases.json`: human-review state, integrity and immutable-field cases.
- `evaluation/benchmark_manifest.json`: dataset versions, distribution and checksums.

## Commands

```bash
python3 -m app.main validate-benchmark --json
python3 -m app.main evaluate-deterministic --json
python3 -m app.main evaluate-agents --mode mock --json
python3 -m app.main evaluate-agents --mode mock-mcp --json
python3 -m app.main evaluate-skills --json
python3 -m app.main evaluate-evidence --json
python3 -m app.main run-security-evaluation --json
python3 -m app.main evaluate-reviews --json
python3 -m app.main evaluate-reproducibility --json
python3 -m app.main run-full-evaluation --json
```

`run-full-evaluation` writes ignored runtime artifacts under `artifacts/evaluation/<run_id>/`. The committed Milestone 6 evidence snapshot is under `docs/evidence/milestone-6/`.

Milestone 7 reads the committed snapshot in the Streamlit UI. The public interface does not depend on ignored runtime evaluation artifacts.
