"""Placeholder interfaces for pathway target lookup tools."""


def get_pathway_target(pathway_type: str) -> int:
    """Return an approved pathway target in a future milestone."""
    raise NotImplementedError(f"Pathway target lookup is not implemented for {pathway_type}.")
