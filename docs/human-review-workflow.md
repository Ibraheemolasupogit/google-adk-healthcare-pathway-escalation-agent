# Human Review Workflow

Milestone 5 implements a backend-only human-review workflow for synthetic demonstration outputs.

The automated Review Agent checks schema, consistency and safety. It does not approve anything. The Human Review Service is the only component that can record an explicit demonstration decision.

Review records are stored as local JSON files under `artifacts/reviews/`, which is ignored by Git. Reviewer identity is a demonstration alias such as `demo-reviewer`; it is not authenticated identity.

Supported decisions:

- `APPROVE`: moves `PENDING` to `APPROVED_FOR_DEMONSTRATION`, keeps `submitted=false`, and records reviewer comments.
- `AMEND`: requires a reason and permitted narrative amendments only, then moves to `AMENDMENT_REQUIRED`.
- `REJECT`: requires a reason and moves to `REJECTED`.

`APPROVED_FOR_DEMONSTRATION` does not mean clinically approved, operationally approved, submitted, or authenticated.

Milestone 6 adds `evaluate-reviews`, which checks valid transitions, immutable-field protection, review-record integrity detection and `submitted=false` preservation for synthetic review scenarios.

Milestone 7 exposes the backend workflow in Streamlit. Reviewer alias entry is explicit, narrative amendments are limited to approved fields, deterministic fields remain read-only, and records remain in ignored runtime storage.
