"""Controlled local demonstration evidence retrieval tools."""

from __future__ import annotations

import json
from pathlib import Path

from schemas.agent import LocalEvidenceDocument
from schemas.case import PathwayCode

from tools.exceptions import DomainValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE_PATH = PROJECT_ROOT / "data" / "evidence" / "local_evidence.json"


def load_local_evidence(path: Path = DEFAULT_EVIDENCE_PATH) -> list[LocalEvidenceDocument]:
    """Load controlled local evidence documents without network access."""
    with path.open(encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, list):
        raise DomainValidationError("local evidence file must contain a list")
    documents = [LocalEvidenceDocument.model_validate(item) for item in payload]
    _validate_unique_evidence_ids(documents)
    return documents


def retrieve_local_evidence(pathway_code: PathwayCode) -> list[LocalEvidenceDocument]:
    """Return demonstration evidence documents for one pathway code."""
    matches = [doc for doc in load_local_evidence() if doc.pathway_code == pathway_code]
    if not matches:
        raise DomainValidationError(f"No local evidence found for {pathway_code}.")
    return matches


def get_local_evidence_by_id(evidence_id: str) -> LocalEvidenceDocument:
    """Return one local evidence document by ID."""
    for document in load_local_evidence():
        if document.evidence_id == evidence_id:
            return document
    raise DomainValidationError(f"Unsupported evidence ID: {evidence_id}.")


def search_policy_evidence(query: str) -> list[str]:
    """Compatibility placeholder; policy search arrives in a later milestone."""
    raise NotImplementedError(f"Policy evidence search is not implemented for {query}.")


def _validate_unique_evidence_ids(documents: list[LocalEvidenceDocument]) -> None:
    seen: set[str] = set()
    for document in documents:
        if document.evidence_id in seen:
            raise DomainValidationError(f"Duplicate evidence ID: {document.evidence_id}")
        seen.add(document.evidence_id)
