# NHS Pathway Escalation and Evidence Agent

## A secure, evidence-grounded Google ADK demonstration with MCP, reusable Agent Skills and human review

The NHS Pathway Escalation and Evidence Agent is a synthetic, evidence-grounded operational review assistant for time-sensitive pathway oversight. It combines deterministic pathway calculations, Google ADK multi-agent orchestration, MCP-based interoperability, reusable Agent Skills, security guardrails, controlled local evidence and explicit human review. The project is submitted for the Agents for Good track because it demonstrates how an agent system can support safer, more consistent operational review while preserving human accountability. It does not provide clinical advice, does not connect to live NHS systems and does not autonomously submit escalations.

## The problem

Operational pathway teams often need to understand whether a time-sensitive pathway case is within target, approaching target, at target, breached or substantially breached. This work can be difficult because pathway status depends on target rules, elapsed time, data completeness, next event timing and local operational context. In a real setting, people also need clear evidence, auditability and escalation discipline. A rushed or unsupported summary could create confusion, while a fully autonomous agent would be inappropriate for a safety-sensitive domain.

## Why existing workflows are difficult

Pathway review requires consistency and traceability. Human reviewers need to see the calculation inputs, understand why a case has a particular operational risk level, know which evidence was retrieved and confirm that any draft escalation is safe to review. Manual processes can be repetitive and fragmented: pathway rules may be checked in one place, evidence in another, escalation wording elsewhere and review approval in a separate workflow. The hard part is not simply generating text. The hard part is preserving deterministic values, limiting the agent boundary, surfacing limitations and making human approval explicit.

## Proposed solution

This project demonstrates a safer pattern: deterministic calculations remain the source of truth, while Google ADK agents coordinate a review workflow around those calculations. The public demo defaults to `mock-mcp` mode. That mode uses Google ADK agent definitions, local MCP-compatible capabilities, controlled local evidence and guardrails without requiring a Gemini API key. Mock mode does not call Gemini and should not be described as a Gemini response. Live Gemini configuration exists as an optional path, but live Gemini execution was not verified for this submission.

## Intended users

The intended demonstration users are operational reviewers, pathway coordinators, digital health teams, AI safety reviewers and competition judges. The system is not intended for patients, diagnosis, treatment planning, medication advice, clinical triage or production NHS deployment. It uses synthetic data only.

## User journey

A reviewer opens the Streamlit demo, sees a persistent synthetic-data warning and selects a prebuilt synthetic case. The primary demo case is `SYN-CANCER-62-003`, a Cancer 62-day scenario that is breached, has elevated operational risk, retrieves evidence and requires human review. The reviewer runs the deterministic assessment, then runs the ADK workflow in `mock-mcp` mode. The interface shows agent steps, tool or MCP invocations, controlled evidence, guardrail status, draft escalation text, a review-agent result and a backend human-review record. The reviewer must enter a demonstration alias before approving, amending or rejecting the draft.

## Architecture

The architecture has seven main boundaries. The deterministic boundary calculates pathway status, elapsed time, breach state, target consumption, variance, operational risk factors and recommended actions. The model boundary is represented by Google ADK agent definitions and mock execution paths. The MCP boundary exposes local case data, pathway rules and policy evidence through bounded MCP-compatible capabilities. The Agent Skills boundary packages reusable functions for pathway identification, risk calculation, evidence retrieval and escalation drafting. The guardrail boundary checks prompt injection, deterministic overrides, unsafe claims, personal data patterns, secrets, review bypass and malformed output. The review boundary stores explicit human decisions with tamper-evident hashes. The deployment boundary packages the Streamlit app for Cloud Run readiness without embedding credentials.

## Agent responsibilities

The Coordinator Agent validates the request and controls the workflow. The Pathway Agent retrieves the pathway rule and deterministic assessment. The Risk Agent preserves the deterministic risk score and explains contributing operational factors. The Evidence Agent retrieves controlled local evidence. The Escalation Agent produces a structured non-clinical draft. The Review Agent checks schema, safety and unsupported claims before the output can be prepared for human review. None of these agents can approve or submit an escalation.

## Google ADK implementation

The agents are defined with Google ADK and use controlled local tools. The workflow is auditable through structured agent steps and tool invocation records. The ADK layer is deliberately constrained: it coordinates around deterministic services rather than replacing them. This distinction matters because the pathway status and risk score must be explainable, repeatable and testable.

## MCP interoperability

The project includes local MCP-compatible servers and a bounded client adapter for case data, pathway rules and policy evidence. In `mock-mcp` mode, the workflow exercises this interoperability boundary while staying offline. The demo therefore shows how an agent can interact with structured external capabilities without connecting to live NHS systems.

## Agent Skills

Reusable Agent Skills are implemented for `identify_pathway`, `calculate_risk`, `retrieve_evidence` and `generate_escalation`. Each skill has metadata, schemas and controlled execution. The skill evaluator checks loading, input validation, output validation and deterministic preservation.

## Deterministic assessment engine

The deterministic engine validates synthetic cases, loads five demonstration pathway rules, calculates elapsed time, classifies breach status, computes an operational risk score from 0 to 10, records risk factors and produces non-clinical recommended actions. These values are not generated by the language model. They are the authoritative values displayed in the UI and preserved by the agent workflow.

## Evidence grounding

Evidence retrieval uses controlled local demonstration records. Each record includes an evidence ID, title, source label, pathway code, summary, type, version, demonstration-only flag and validation-required flag. The system clearly distinguishes retrieved evidence from deterministic calculation and agent-generated narrative. Evidence is not presented as current authoritative NHS guidance.

## Security guardrails

The guardrail service checks inputs, evidence and drafts for prompt injection, deterministic override attempts, review bypass, clinical advice language, autonomous-action claims, personal data patterns, secrets and malformed output. These checks are pragmatic deterministic controls, not perfect protection. The UI uses safe errors, redaction, read-only deterministic values, approved narrative amendments only and size-limited downloads.

## Human-in-the-loop workflow

Every assessment and escalation draft requires human review. The backend review workflow supports `APPROVED_FOR_DEMONSTRATION`, `AMENDMENT_REQUIRED` and `REJECTED` decisions. Reviewer identity is a demonstration alias and is not authenticated identity. Review records preserve `submitted=false` and `authenticated_identity=false`. Integrity checks compare review, draft and deterministic-assessment hashes.

## Evaluation methodology

Evaluation uses controlled synthetic data only. The committed benchmark contains 30 cases, six per supported pathway: Cancer Two Week Wait, Cancer Faster Diagnosis 28-day, Cancer 62-day, RTT 18-week and Urgent and Emergency Care 4-hour. Automated evaluators cover deterministic exact-match behavior, mock and mock-MCP agent preservation, execution-mode parity, Agent Skills, evidence grounding, security cases, review controls and reproducibility.

## Evaluation results

The committed Milestone 6 evidence snapshot reports benchmark version `2026-07-milestone-6-demo-v1`, run ID `EVAL-RUN-20260704145457-4548481e`, 30 benchmark cases and an overall controlled benchmark pass rate of 1.0. Deterministic pathway accuracy, breach-status accuracy, risk-level accuracy, risk-score exact-match rate, action-code accuracy and schema-compliance rate are all 1.0 on the controlled benchmark. Mock and mock-MCP deterministic-preservation, evidence-grounding and human-review-enforcement rates are 1.0. Skill load, input validation, output validation and deterministic preservation are 1.0. Evidence grounding, review controls, reproducibility, security precision, security recall, security F1 and blocking-case pass rate are 1.0 on their controlled datasets. These results are not production performance claims.

## Demonstration walkthrough

The recommended demo starts in presentation mode with `SYN-CANCER-62-003`. The presenter shows the safety banner, runs deterministic assessment, points to breach status `BREACHED`, risk score `7.5` and risk level `CRITICAL`, then runs the `mock-mcp` agent workflow. The presenter shows ADK steps, MCP/tool invocations, evidence records, guardrail status and human review. The final section shows committed evaluation evidence and limitations.

## Responsible-AI considerations

The project is synthetic-only, non-clinical and review-gated. It avoids credential entry in the UI, redacts common secret patterns, blocks real patient-identifiable patterns where practical, requires human review and states limitations visibly. It does not claim production readiness, clinical safety, real NHS integration or authenticated approval.

## Limitations

The system uses demonstration pathway targets, synthetic data and local evidence. It does not use real NHS operational feeds. It does not provide clinical diagnosis, treatment advice or medication advice. It does not prove production safety. Live Gemini execution was not verified. Cloud Run deployment readiness is documented, but deployment was not performed. Guardrails are not exhaustive, and local hashes are tamper-evident checks rather than digital signatures.

## Future work

Future work would include live Gemini validation in a secured environment, authenticated reviewer identity, production governance review, stronger monitoring, improved threat modelling, deployment hardening, real policy validation with authorised sources and usability testing with appropriate operational stakeholders.

## Conclusion

The NHS Pathway Escalation and Evidence Agent shows how an agent system can support responsible operational review by combining deterministic calculations, evidence grounding, ADK orchestration, MCP interoperability, Agent Skills, guardrails and human-in-the-loop control. Its main contribution is not autonomous decision-making. Its value is demonstrating a safer architecture where agents assist, deterministic logic remains auditable and humans remain accountable.

## Repository and demo placeholders

- GitHub repository: [add public repository URL]
- Kaggle write-up URL: [add after submission]
- YouTube demo URL: [add after upload]
- Deployed demo URL: [optional, add only if actually deployed]

