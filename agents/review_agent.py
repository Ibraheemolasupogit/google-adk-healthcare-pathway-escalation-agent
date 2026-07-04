"""Review agent placeholder for schema, safety, and approval routing checks."""

from schemas.escalation import EscalationRecommendation


class ReviewAgent:
    """Planned agent that validates completeness and routes human review."""

    def validate_for_review(self, draft: EscalationRecommendation) -> EscalationRecommendation:
        """Validate draft completeness and safety before human approval."""
        raise NotImplementedError("Review validation will be implemented in a later milestone.")
