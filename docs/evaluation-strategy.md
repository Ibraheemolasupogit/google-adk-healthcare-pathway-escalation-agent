# Evaluation Strategy

Future evaluation will use synthetic fixtures and expected outputs to measure:

- **Pathway-target retrieval accuracy:** correct mapping from synthetic pathway cases to validated target definitions.
- **Breach-calculation accuracy:** deterministic elapsed-time and breach-status calculations.
- **Risk-classification accuracy:** agreement with expected operational risk labels and contributing factors.
- **Schema compliance:** all generated outputs validate against Pydantic schemas.
- **Evidence grounding:** recommendations cite controlled evidence and distinguish retrieved facts from inference.
- **Tool-selection accuracy:** agents choose the appropriate case, pathway, and evidence tools.
- **Unsupported-claim rate:** review checks identify claims without evidence support.
- **Human-review enforcement:** every escalation requires human review and cannot be finalised autonomously.
- **Prompt-injection resistance:** malicious case text or retrieved content cannot override safety rules.
- **Reproducibility:** documented commands reproduce validation and evaluation results.
