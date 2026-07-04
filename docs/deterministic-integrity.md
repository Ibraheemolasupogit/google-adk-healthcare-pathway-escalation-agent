# Deterministic Integrity

Milestone 5 adds canonical JSON serialisation and SHA-256 hashes for:

- deterministic assessments;
- agent drafts;
- human-review records.

The review service verifies hashes before decisions. If the deterministic assessment, draft or stored review record changes unexpectedly, the review is marked `INVALIDATED` and approval is blocked.

This is tamper-evident local metadata, not a digital-signature system and not authenticated identity.
