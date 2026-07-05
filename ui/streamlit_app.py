"""Streamlit public demonstration app."""

from __future__ import annotations

from typing import cast

import streamlit as st
from schemas.agent import AgentExecutionResult, ExecutionMode
from schemas.assessment import PathwayAssessment
from schemas.review import HumanReviewDecision, HumanReviewRecord
from services.security_utils import AMENDABLE_REVIEW_FIELDS

from ui.components import (
    render_agent,
    render_architecture_and_limitations,
    render_assessment,
    render_case,
    render_evaluation,
    render_evidence,
    render_guardrails,
    render_header,
    render_review,
)
from ui.config import PRIMARY_DEMO_CASE_ID, load_ui_config
from ui.demo_service import (
    build_download,
    decide_review,
    get_case_summary,
    get_evidence,
    get_guardrail_result,
    list_case_options,
    load_evaluation_evidence,
    prepare_review,
    run_agent,
    run_deterministic,
    verify_review,
)
from ui.formatting import concise_error
from ui.state import reset_case_state


def main() -> None:
    """Run the Streamlit app."""
    config = load_ui_config()
    st.set_page_config(
        page_title=config.title,
        page_icon=":material/medical_services:",
        layout="wide",
    )
    render_header(config.title, config.subtitle)

    cases = list_case_options(config.presentation_mode)
    default_case_id = PRIMARY_DEMO_CASE_ID if config.presentation_mode else cases[0]["case_id"]
    case_ids = [case["case_id"] for case in cases]
    selected_case_id = st.sidebar.selectbox(
        "Synthetic case",
        case_ids,
        index=case_ids.index(default_case_id) if default_case_id in case_ids else 0,
    )
    reset_case_state(st.session_state, selected_case_id)
    st.sidebar.caption("Offline demonstration mode. No Gemini or NHS systems are called.")
    mode = st.sidebar.radio(
        "Execution mode",
        [ExecutionMode.MOCK_MCP.value, ExecutionMode.MOCK.value],
        index=0,
        help="mock-MCP is the default public demonstration mode.",
    )

    tabs = st.tabs(
        [
            "Overview",
            "Select Case",
            "Deterministic Assessment",
            "Agent Workflow",
            "Evidence",
            "Security and Guardrails",
            "Human Review",
            "Evaluation Evidence",
            "Architecture and Limitations",
        ]
    )

    with tabs[0]:
        st.write(
            "This interface demonstrates synthetic pathway review using deterministic "
            "calculations, Google ADK agent definitions, local MCP capabilities, controlled "
            "evidence, guardrails and a backend human-review workflow."
        )
        st.write("Primary recommended demo case:", f"`{PRIMARY_DEMO_CASE_ID}`")
        st.write("Presentation mode:", config.presentation_mode)
        st.write("Default execution mode:", config.default_execution_mode.value)

    try:
        case_payload = get_case_summary(selected_case_id)
        with tabs[1]:
            render_case(case_payload)

        with tabs[2]:
            if st.button("Run deterministic assessment", key="run_det"):
                st.session_state["deterministic_result"] = run_deterministic(selected_case_id)
            assessment = cast(
                PathwayAssessment,
                st.session_state.get("deterministic_result")
                or run_deterministic(str(selected_case_id)),
            )
            st.session_state["deterministic_result"] = assessment
            render_assessment(assessment)
            st.download_button(
                "Download deterministic assessment JSON",
                build_download(assessment, "deterministic-assessment"),
                file_name=f"{selected_case_id}-deterministic-assessment.json",
                mime="application/json",
            )

        with tabs[3]:
            if st.button("Run agent workflow", key="run_agent"):
                st.session_state["agent_result"] = run_agent(
                    str(selected_case_id), ExecutionMode(mode)
                )
            agent_state = st.session_state.get("agent_result")
            if agent_state is not None:
                result = cast(AgentExecutionResult, agent_state)
                render_agent(result)
                st.download_button(
                    "Download agent execution JSON",
                    build_download(result, "agent-execution"),
                    file_name=f"{selected_case_id}-agent-execution.json",
                    mime="application/json",
                )
            else:
                st.info("Run the agent workflow to display ADK and MCP steps.")

        with tabs[4]:
            render_evidence(get_evidence(str(selected_case_id), config.max_evidence_records))

        with tabs[5]:
            agent_result = cast(AgentExecutionResult | None, st.session_state.get("agent_result"))
            guardrail_result = get_guardrail_result(
                st.session_state["deterministic_result"], agent_result
            )
            render_guardrails(guardrail_result)

        with tabs[6]:
            if st.button("Prepare review", key="prepare_review"):
                record = prepare_review(str(selected_case_id), ExecutionMode(mode), config)
                st.session_state["review_id"] = record.review_id
                st.session_state["review_record"] = record
            record_state = st.session_state.get("review_record")
            if record_state is not None:
                review_record = cast(HumanReviewRecord, record_state)
                render_review(review_record)
                reviewer_alias = st.text_input("Reviewer alias", value="")
                decision = st.selectbox(
                    "Decision",
                    ["approve for demonstration", "request amendment", "reject"],
                )
                comments = st.text_area("Comments or reason", value="")
                amendment_field = None
                amendment_value = None
                if decision == "request amendment":
                    amendment_field = st.selectbox(
                        "Approved narrative amendment field",
                        sorted(AMENDABLE_REVIEW_FIELDS),
                    )
                    amendment_value = st.text_area("Narrative amendment text", value="")
                    st.caption(
                        "Deterministic fields such as risk score, breach status and target are "
                        "read-only and cannot be amended."
                    )
                if st.button("Apply review decision", key="decide_review"):
                    if not reviewer_alias:
                        st.error("Reviewer alias is required for demonstration review decisions.")
                    else:
                        mapped = {
                            "approve for demonstration": HumanReviewDecision.APPROVE,
                            "request amendment": HumanReviewDecision.AMEND,
                            "reject": HumanReviewDecision.REJECT,
                        }[decision]
                        updated = decide_review(
                            review_record.review_id,
                            mapped,
                            reviewer_alias,
                            config,
                            comments=comments if mapped == HumanReviewDecision.APPROVE else None,
                            reason=comments if mapped != HumanReviewDecision.APPROVE else None,
                            amendment_field=amendment_field,
                            amendment_value=amendment_value,
                        )
                        st.session_state["review_record"] = updated
                        render_review(updated)
                if st.button("Verify review integrity", key="verify_review"):
                    st.json(verify_review(review_record.review_id, config))
                st.download_button(
                    "Download human-review record JSON",
                    build_download(review_record, "human-review-record"),
                    file_name=f"{review_record.review_id}.json",
                    mime="application/json",
                )
            else:
                st.info("Prepare a review before applying a demonstration decision.")

        with tabs[7]:
            eval_evidence = load_evaluation_evidence()
            render_evaluation(eval_evidence)
            st.download_button(
                "Download evaluation benchmark summary JSON",
                build_download(eval_evidence["benchmark"], "evaluation-summary"),
                file_name="milestone-6-benchmark-summary.json",
                mime="application/json",
            )

        with tabs[8]:
            render_architecture_and_limitations()
    except Exception as exc:
        st.error(concise_error(exc))


if __name__ == "__main__":
    main()
