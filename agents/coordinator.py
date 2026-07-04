"""Coordinator agent placeholder for future Google ADK orchestration."""

from schemas.assessment import PathwayAssessment
from schemas.case import SyntheticPathwayCase


class CoordinatorAgent:
    """Planned workflow controller for future Google ADK orchestration."""

    def assess_case(self, case: SyntheticPathwayCase) -> PathwayAssessment:
        """Delegate future agent workflow steps around deterministic assessment."""
        raise NotImplementedError("Agent orchestration will be implemented in a later milestone.")
