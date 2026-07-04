"""Evidence agent placeholder for controlled evidence retrieval."""

from schemas.case import SyntheticPathwayCase


class EvidenceAgent:
    """Planned agent that retrieves source-attributed policy evidence."""

    def retrieve_evidence(self, case: SyntheticPathwayCase) -> list[str]:
        """Retrieve controlled evidence and source metadata."""
        raise NotImplementedError("Evidence retrieval will be implemented in a later milestone.")
