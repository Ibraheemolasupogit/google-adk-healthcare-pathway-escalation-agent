# Responsible AI Statement

This project is a synthetic demonstration only. It does not provide clinical advice, diagnosis, treatment recommendations, medication advice, operational authority or autonomous escalation.

## Synthetic Data

All cases are synthetic and marked as synthetic. The UI does not provide free-text patient case entry. Public demonstration commands use prebuilt synthetic cases.

## Non-Clinical Scope

The risk score is operational and deterministic. It is not a clinical risk score and must not be used for diagnosis, triage or treatment.

## Deterministic Source of Truth

Pathway status, elapsed time, breach status, variance, target consumption, risk score and recommended action codes are calculated by deterministic services. Agent-generated narrative must preserve these values.

## Controlled Evidence

Evidence is local demonstration evidence with source labels, versions, demonstration-only flags and validation-required flags. It is not current authoritative NHS guidance.

## Least Privilege

The public UI defaults to offline `mock-mcp` mode. It does not require Gemini credentials and does not connect to live NHS systems.

## Prompt-Injection Controls

Guardrails check prompt injection, deterministic override attempts, review bypass, unsupported claims and unsafe instructions. These controls are not exhaustive.

## Personal-Data Protections

The project rejects or flags common personal-data patterns and avoids free-text patient entry in the public UI. It must not be used with real patient-identifiable data.

## Secret Redaction

Common secret patterns are redacted from UI errors and downloads. Credentials are not entered through the UI and are not stored in session state.

## Human Approval

Every output requires human review. Review records remain `submitted=false` and `authenticated_identity=false`. A demonstration approval is not clinical, operational or authenticated approval.

## Transparent Limitations

The repository and UI state limitations visibly: synthetic data only, no live NHS integration, no verified live Gemini execution, no Cloud Run deployment, non-exhaustive guardrails and no production readiness claim.

