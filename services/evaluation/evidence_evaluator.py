"""Evidence grounding evaluator."""

from __future__ import annotations

from datetime import UTC, datetime

from schemas.case import PathwayCode
from schemas.evaluation import EvaluationFailure, EvidenceGroundingResult
from tools.evidence_tools import retrieve_local_evidence

from services.evaluation.benchmark_loader import load_evidence_grounding_cases
from services.evaluation.common import failure, metric, suite_result
from services.guardrail_service import GuardrailService


def evaluate_evidence() -> EvidenceGroundingResult:
    """Evaluate controlled local evidence grounding."""
    started = datetime.now(UTC)
    cases = load_evidence_grounding_cases()
    failures: list[EvaluationFailure] = []
    grounded = metadata = flags = injection_safe = 0
    for item in cases:
        docs = retrieve_local_evidence(PathwayCode(item["pathway_code"]))
        actual_ids = [doc.evidence_id for doc in docs]
        if actual_ids == item["expected_evidence_ids"]:
            grounded += 1
        else:
            failures.append(
                failure(
                    item["pathway_code"],
                    "evidence_ids",
                    item["expected_evidence_ids"],
                    actual_ids,
                    "evidence ID mismatch",
                )
            )
        if all(doc.source_label and doc.source_url_placeholder for doc in docs):
            metadata += 1
        if all(doc.demonstration_only and doc.validation_required for doc in docs):
            flags += 1
        if all(GuardrailService().check_evidence(doc).passed for doc in docs):
            injection_safe += 1
    total = len(cases)
    metrics = [
        metric("evidence_grounding_rate", grounded / total, 1.0),
        metric("source_metadata_rate", metadata / total, 1.0),
        metric("demonstration_flag_rate", flags / total, 1.0),
        metric("evidence_injection_safe_rate", injection_safe / total, 1.0),
    ]
    return EvidenceGroundingResult.model_validate(
        suite_result(
            started_at=started,
            case_count=total,
            failures=failures,
            metrics=metrics,
            execution_mode="evidence",
        ).model_dump()
    )
