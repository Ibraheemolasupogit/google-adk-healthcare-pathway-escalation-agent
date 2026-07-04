"""Risk agent placeholder for deterministic operational risk scoring."""

from schemas.assessment import PathwayAssessment
from schemas.case import SyntheticPathwayCase


class RiskAgent:
    """Planned agent that calculates explainable operational risk."""

    def calculate_risk(self, case: SyntheticPathwayCase) -> PathwayAssessment:
        """Calculate deterministic risk and contributing factors."""
        raise NotImplementedError("Risk scoring will be implemented in a later milestone.")
