"""Placeholder interfaces for synthetic case data tools."""

from schemas.case import SyntheticPathwayCase


def load_synthetic_case(case_id: str) -> SyntheticPathwayCase:
    """Load a synthetic case by identifier in a future milestone."""
    raise NotImplementedError(f"Synthetic case loading is not implemented for {case_id}.")
