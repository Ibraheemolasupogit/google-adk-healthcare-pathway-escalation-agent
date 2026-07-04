"""Domain exceptions for deterministic pathway tooling."""


class DomainValidationError(ValueError):
    """Raised when local deterministic domain data fails validation."""


class PathwayRuleNotFoundError(KeyError):
    """Raised when a pathway rule cannot be found."""


class CaseNotFoundError(KeyError):
    """Raised when a synthetic case cannot be found."""
