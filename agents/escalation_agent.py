"""Escalation agent placeholder for structured escalation drafts."""

from schemas.assessment import PathwayAssessment
from schemas.escalation import EscalationRecommendation


class EscalationAgent:
    """Planned agent that drafts recommendations without sending them."""

    def generate_draft(self, assessment: PathwayAssessment) -> EscalationRecommendation:
        """Generate a structured draft that remains subject to human approval."""
        raise NotImplementedError("Escalation drafting will be implemented in a later milestone.")
