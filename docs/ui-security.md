# UI Security

The Streamlit UI is a public synthetic demonstration surface.

Controls:

- Prebuilt synthetic case selector only.
- No free-text patient case entry.
- No credential input boxes.
- No secrets stored in session state.
- Live mode disabled by default.
- Mock-MCP default execution.
- Download payloads are validated, size-limited and redacted.
- Arbitrary local file downloads are not exposed.
- Path traversal is rejected in identifiers and download labels.
- Deterministic values are displayed read-only.
- Amendments are limited to approved narrative fields.
- Review state changes go through `HumanReviewService`.
- User-facing errors remove stack traces and local paths.
- Unsafe HTML rendering is not used.

The deterministic guardrails are pragmatic checks and are not exhaustive protection against all malicious input.

