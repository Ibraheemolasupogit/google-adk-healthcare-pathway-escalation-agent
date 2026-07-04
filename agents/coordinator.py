"""Coordinator agent placeholder for future Google ADK orchestration."""

from schemas.case import SyntheticPathwayCase
from schemas.escalation import EscalationRecommendation


class CoordinatorAgent:
    """Planned workflow controller for specialist agents."""

    def draft_escalation(self, case: SyntheticPathwayCase) -> EscalationRecommendation:
        """Delegate future pathway, risk, evidence, escalation, and review steps."""
        raise NotImplementedError("Coordinator workflow will be implemented in a later milestone.")
