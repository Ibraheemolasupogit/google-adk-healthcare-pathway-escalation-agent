"""Formatting, redaction and download helpers for the UI."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel
from services.security_utils import contains_path_traversal, redact_secrets
from tools.exceptions import DomainValidationError

MAX_DOWNLOAD_BYTES = 250_000


def safe_text(value: Any) -> str:
    """Return concise text with common secret patterns redacted."""
    return redact_secrets(str(value))


def to_json_bytes(payload: BaseModel | dict[str, Any] | list[Any], label: str) -> bytes:
    """Validate and serialise a safe demonstration download."""
    if contains_path_traversal(label):
        raise DomainValidationError("download label cannot contain path traversal")
    if isinstance(payload, BaseModel):
        serialisable: Any = payload.model_dump(mode="json")
    else:
        serialisable = payload
    text = json.dumps(serialisable, indent=2, sort_keys=True, default=str)
    redacted = redact_secrets(text)
    data = redacted.encode("utf-8")
    if len(data) > MAX_DOWNLOAD_BYTES:
        raise DomainValidationError("download exceeds maximum demonstration size")
    if isinstance(serialisable, dict):
        if serialisable.get("demonstration_only") is not True:
            raise DomainValidationError("download must be marked demonstration-only")
        if "synthetic" in serialisable and serialisable.get("synthetic") is not True:
            raise DomainValidationError("download must be synthetic")
    return data


def concise_error(exc: Exception) -> str:
    """Return a user-facing error without paths or stack traces."""
    message = safe_text(exc)
    for separator in ["/Users/", "\\Users\\", "Traceback", 'File "']:
        message = message.replace(separator, "[local-path-redacted]")
    return f"Unable to complete the safe demonstration action: {message}"
