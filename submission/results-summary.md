# Results Summary

This summary uses committed evidence from `docs/evidence/milestone-6/`.

## Benchmark Evaluation Results

- Benchmark version: `2026-07-milestone-6-demo-v1`.
- Evaluation run ID: `EVAL-RUN-20260704145457-4548481e`.
- Benchmark size: 30 synthetic cases.
- Pathway distribution: six cases each for `CANCER_2WW`, `CANCER_FDS_28`, `CANCER_62`, `RTT_18_WEEK` and `UEC_4_HOUR`.
- Overall controlled benchmark pass rate: `1.0`.

## Deterministic Assessment

- Pathway accuracy: `1.0`.
- Breach-status accuracy: `1.0`.
- Risk-level accuracy: `1.0`.
- Risk-score exact-match rate: `1.0`.
- Action-code accuracy: `1.0`.
- Schema-compliance rate: `1.0`.

## Agent Results

- Mock deterministic-preservation rate: `1.0`.
- Mock-MCP deterministic-preservation rate: `1.0`.
- Mock evidence-grounding rate: `1.0`.
- Mock-MCP evidence-grounding rate: `1.0`.
- Human-review-enforcement rate: `1.0` in both mock modes.
- Execution-mode parity rate: `1.0`.

## Skill Results

- Skill load rate: `1.0`.
- Input validation rate: `1.0`.
- Output validation rate: `1.0`.
- Deterministic-preservation rate: `1.0`.

## Evidence, Security, Review and Reproducibility

- Evidence-grounding rate: `1.0`.
- Security precision: `1.0`.
- Security recall: `1.0`.
- Security F1: `1.0`.
- Blocking-case pass rate: `1.0`.
- Review valid-transition rate: `1.0`.
- Review immutable-field protection rate: `1.0`.
- Review integrity-detection rate: `1.0`.
- Review submitted-false rate: `1.0`.
- Deterministic reproducibility rate: `1.0`.
- Mock reproducibility rate: `1.0`.
- Mock-MCP reproducibility rate: `1.0`.

## Repository Test Results

Milestone 8 local validation reported 118 tests passing with 85 percent coverage. This repository test result is separate from the synthetic benchmark evaluation result above.

## Limitations

These are controlled synthetic benchmark results. They are not production results and do not measure production NHS readiness, clinical safety, live Gemini behaviour, real-world data quality or deployed Cloud Run reliability.
