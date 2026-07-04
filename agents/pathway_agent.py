"""Pathway agent placeholder for target identification."""

from schemas.assessment import PathwayAssessment
from schemas.case import SyntheticPathwayCase


class PathwayAgent:
    """Planned agent that identifies pathway type and approved targets."""

    def assess_pathway(self, case: SyntheticPathwayCase) -> PathwayAssessment:
        """Determine applicable pathway target without inventing target values."""
        raise NotImplementedError("Pathway assessment will be implemented in a later milestone.")
