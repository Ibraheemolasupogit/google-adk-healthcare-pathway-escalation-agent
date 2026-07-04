# Threat Model

## Accidental Use of Personal Data

- **Threat:** A user includes real patient-identifiable information in a case.
- **Mitigation:** Require synthetic flags, validate disallowed identifier fields, document synthetic-only usage, and add future input scanning.
- **Residual risk:** Free-text fields may still contain identifiers until stronger detection is implemented.

## Prompt Injection

- **Threat:** Case text attempts to override system instructions or bypass review.
- **Mitigation:** Treat user text as data, constrain outputs with schemas, and route all drafts through review.
- **Residual risk:** Future model behavior requires continuous adversarial testing.

## Malicious Retrieved Content

- **Threat:** Evidence content contains instructions that manipulate the agent.
- **Mitigation:** Treat retrieved content as untrusted evidence, strip executable instructions, and separate evidence from control prompts.
- **Residual risk:** Retrieval sources must remain carefully curated.

## Unsupported Pathway Claims

- **Threat:** The system invents pathway targets or operational rules.
- **Mitigation:** Use controlled pathway target configuration and surface unsupported claims.
- **Residual risk:** Target files can become stale and require governance.

## Hallucinated Evidence

- **Threat:** The model fabricates supporting evidence.
- **Mitigation:** Require source metadata, controlled retrieval, and review-agent checks.
- **Residual risk:** Future generation must be evaluated for grounding failures.

## Excessive Tool Permissions

- **Threat:** Tools access or modify data beyond their purpose.
- **Mitigation:** Apply least-privilege tools, narrow MCP server responsibilities, and auditable tool calls.
- **Residual risk:** Deployment configuration errors can still expand permissions.

## Secret Exposure

- **Threat:** API keys or cloud credentials are committed or logged.
- **Mitigation:** Use `.env.example` placeholders, ignore `.env`, and externalise secrets.
- **Residual risk:** Developers must avoid pasting secrets into docs, logs, or issue trackers.

## Unsafe Autonomous Escalation

- **Threat:** The system sends or finalises an escalation without human approval.
- **Mitigation:** Require `human_review_required`, block autonomous sending, and record `approved_by_human`.
- **Residual risk:** Future integrations must enforce approval at every boundary.

## Audit-Log Leakage

- **Threat:** Audit logs expose sensitive text or secrets.
- **Mitigation:** Avoid real patient data, redact secrets, and limit audit retention and access.
- **Residual risk:** Logs need ongoing privacy review as features expand.

## Denial-of-Service Through Oversized Inputs

- **Threat:** Very large cases or evidence payloads exhaust resources.
- **Mitigation:** Add input-size limits, timeout controls, and safe failure behavior.
- **Residual risk:** Limits require tuning against future deployment capacity.

## Agent Prompt Injection and Tool Misuse

- **Threat:** User input or retrieved evidence attempts to override instructions, tools, deterministic values or human-review controls.
- **Mitigation:** Use maximum input size, workflow step limits, tool-call limits, local evidence only, deterministic-value review checks, prohibited-language checks and schema validation.
- **Residual risk:** Live model behavior will require additional adversarial testing before any public deployment.

## Malformed Model Output or Model Unavailability

- **Threat:** Live model output is invalid, unavailable or tries to bypass required schemas.
- **Mitigation:** Mock mode is used for tests, live mode is credential-gated, malformed output fails validation, and invalid outputs are not presented as successful.
- **Residual risk:** Live execution needs operational monitoring and timeout configuration in later milestones.
