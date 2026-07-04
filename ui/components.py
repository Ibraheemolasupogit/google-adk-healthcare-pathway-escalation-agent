"""Reusable Streamlit rendering components."""

from __future__ import annotations

from typing import Any

import streamlit as st
from schemas.agent import AgentExecutionResult, LocalEvidenceDocument
from schemas.assessment import PathwayAssessment
from schemas.review import HumanReviewRecord
from schemas.security import GuardrailResult

from ui.config import CLINICAL_DISCLAIMER, SAFETY_BANNER
from ui.help_content import ARCHITECTURE_SUMMARY, BADGES, LIMITATIONS, WORKFLOW_STEPS


def render_header(title: str, subtitle: str) -> None:
    """Render the public demonstration header."""
    st.title(title)
    st.caption(subtitle)
    st.warning(SAFETY_BANNER)
    st.info(CLINICAL_DISCLAIMER)
    st.write(" ".join(f"`{badge}`" for badge in BADGES))


def render_case(case: dict[str, Any]) -> None:
    """Render selected synthetic case fields."""
    st.subheader("Selected Synthetic Case")
    st.json(
        {
            "case_id": case["case_id"],
            "pathway": case["pathway_code"],
            "current_stage": case["current_stage"],
            "referral_or_arrival_datetime": case["referral_or_arrival_datetime"],
            "assessment_datetime": case["assessment_datetime"],
            "priority": case["priority"],
            "operational_flags": case["operational_flags"],
            "next_event_datetime": case.get("next_event_datetime"),
            "synthetic": case["synthetic"],
        }
    )


def render_assessment(assessment: PathwayAssessment) -> None:
    """Render deterministic assessment values as read-only output."""
    st.subheader("Deterministic Assessment")
    cols = st.columns(4)
    cols[0].metric("Breach status", assessment.breach_status.value)
    cols[1].metric("Risk score", assessment.risk_score)
    cols[2].metric("Risk level", assessment.risk_level.value)
    cols[3].metric("Target consumption", f"{assessment.target_consumption_percent}%")
    st.json(
        {
            "pathway_name": assessment.pathway_name,
            "target": assessment.target.model_dump(mode="json"),
            "elapsed_time": assessment.elapsed_time.model_dump(mode="json"),
            "variance_from_target": assessment.variance_from_target,
            "risk_factors": [item.model_dump(mode="json") for item in assessment.risk_factors],
            "recommended_actions": [
                item.model_dump(mode="json") for item in assessment.recommended_actions
            ],
            "audit_trace_id": assessment.audit_trace_id,
            "demonstration_only": assessment.demonstration_only,
            "human_review_required": assessment.human_review_required,
        }
    )
    st.caption("These values are deterministic and are not calculated by the language model.")


def render_agent(result: AgentExecutionResult) -> None:
    """Render safe agent workflow summaries."""
    st.subheader("Agent Workflow")
    st.write(" -> ".join(WORKFLOW_STEPS))
    st.json(
        {
            "execution_mode": result.execution_mode.value,
            "request_id": result.request_id,
            "audit_trace_id": result.audit_trace_id,
            "human_review_required": result.human_review_required,
            "review_status": result.review_status.value,
            "warnings": result.warnings,
            "model_metadata": result.model_metadata,
        }
    )
    st.write("Workflow sequence")
    st.dataframe(
        [
            {
                "sequence": step.sequence,
                "agent": step.agent_name.value,
                "responsibility": step.responsibility,
                "input": step.input_summary,
                "output": step.output_summary,
            }
            for step in result.agent_steps
        ],
        hide_index=True,
    )
    st.write("Tool and MCP invocations")
    st.dataframe(
        [
            {
                "sequence": item.sequence,
                "agent": item.agent_name.value,
                "tool": item.tool_name,
                "success": item.success,
                "input": item.input_summary,
                "output": item.output_summary,
            }
            for item in result.tool_invocations
        ],
        hide_index=True,
    )
    st.write("Draft escalation")
    st.json(result.agent_draft.model_dump(mode="json"))
    st.write("Automated Review Agent result")
    st.json(result.review_result.model_dump(mode="json"))


def render_evidence(evidence: list[LocalEvidenceDocument]) -> None:
    """Render controlled local evidence records."""
    st.subheader("Controlled Evidence")
    st.caption("Retrieved evidence is local demonstration content, not current NHS guidance.")
    st.dataframe(
        [
            {
                "evidence_id": item.evidence_id,
                "title": item.title,
                "source_label": item.source_label,
                "pathway_code": item.pathway_code.value,
                "summary": item.summary,
                "evidence_type": item.evidence_type,
                "version": item.version,
                "demonstration_only": item.demonstration_only,
                "validation_required": item.validation_required,
            }
            for item in evidence
        ],
        hide_index=True,
    )


def render_guardrails(result: GuardrailResult) -> None:
    """Render guardrail status and findings."""
    st.subheader("Security and Guardrails")
    st.json(
        {
            "passed": result.passed,
            "safe_for_human_review": result.safe_for_human_review,
            "finding_count": len(result.findings),
            "deterministic_integrity": "checked",
            "prompt_injection_protection": "deterministic rules applied",
            "personal_data_protection": "synthetic-data constraints and pattern checks applied",
            "secret_redaction": "common secret patterns are redacted from display/downloads",
            "not_exhaustive": True,
        }
    )
    st.dataframe(
        [
            {
                "severity": finding.severity.value,
                "category": finding.category.value,
                "field": finding.field,
                "message": finding.message,
            }
            for finding in result.findings
        ],
        hide_index=True,
    )


def render_review(record: HumanReviewRecord) -> None:
    """Render a human-review record."""
    st.subheader("Human Review Record")
    st.json(
        {
            "review_id": record.review_id,
            "status": record.status.value,
            "decision": record.decision.value if record.decision else None,
            "submitted": record.submitted,
            "authenticated_identity": record.authenticated_identity,
            "draft_hash": record.draft_hash,
            "deterministic_assessment_hash": record.deterministic_assessment_hash,
            "record_hash": record.integrity.record_hash,
        }
    )
    st.write("Review history")
    st.dataframe(
        [
            {
                "sequence": item.sequence,
                "status": item.status.value,
                "event": item.event,
                "reviewer": item.reviewer_id,
                "comments": item.comments,
            }
            for item in record.history
        ],
        hide_index=True,
    )


def render_evaluation(evidence: dict[str, Any]) -> None:
    """Render committed Milestone 6 evidence."""
    benchmark = evidence["benchmark"]
    st.subheader("Evaluation Evidence")
    st.json(
        {
            "benchmark_version": benchmark["benchmark_version"],
            "run_id": benchmark["run_id"],
            "case_count": benchmark["case_count"],
            "case_distribution": benchmark["case_distribution"],
            "overall_pass_rate": benchmark["overall_pass_rate"],
            "failed_case_ids": benchmark["failed_case_ids"],
        }
    )
    st.dataframe(evidence["metrics"], hide_index=True)
    st.markdown(evidence["limitations"])


def render_architecture_and_limitations() -> None:
    """Render architecture summary and limitations."""
    st.subheader("Architecture")
    st.write(" -> ".join(WORKFLOW_STEPS))
    st.json(ARCHITECTURE_SUMMARY)
    st.subheader("Limitations")
    for item in LIMITATIONS:
        st.write(f"- {item}")
