"""Tests for the Milestone 7 Streamlit UI service layer."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from schemas.agent import ExecutionMode
from schemas.review import HumanReviewDecision
from tools.exceptions import DomainValidationError
from ui import components
from ui.config import (
    CLINICAL_DISCLAIMER,
    PRIMARY_DEMO_CASE_ID,
    SAFETY_BANNER,
    UIConfig,
    available_public_modes,
    load_ui_config,
)
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
)
from ui.formatting import concise_error
from ui.health import run_health_checks
from ui.help_content import ARCHITECTURE_SUMMARY, LIMITATIONS
from ui.state import reset_case_state


def config_for(tmp_path: Path) -> UIConfig:
    """Return a temp review-store config."""
    return UIConfig(review_store_path=tmp_path / "reviews")


def test_streamlit_app_imports_and_default_config_is_safe() -> None:
    module = importlib.import_module("ui.streamlit_app")
    config = load_ui_config()

    assert module is not None
    assert config.default_execution_mode == ExecutionMode.MOCK_MCP
    assert config.enable_live_mode is False
    assert ExecutionMode.LIVE not in available_public_modes(config)


def test_public_safety_text_exists() -> None:
    assert "synthetic demonstration data only" in SAFETY_BANNER
    assert "does not provide clinical advice" in SAFETY_BANNER
    assert "not operational NHS guidance" in CLINICAL_DISCLAIMER


def test_case_selector_uses_synthetic_cases_only() -> None:
    cases = list_case_options()

    assert cases
    assert all(row["synthetic"] == "True" for row in cases)
    assert not any("patient" in row["case_id"].lower() for row in cases)


def test_presentation_mode_selects_primary_case_first() -> None:
    cases = list_case_options(presentation_mode=True)

    assert cases[0]["case_id"] == PRIMARY_DEMO_CASE_ID


def test_deterministic_assessment_values_are_read_only_outputs() -> None:
    assessment = run_deterministic("SYN-CANCER-62-003")
    payload = assessment.model_dump(mode="json")

    assert payload["risk_score"] == assessment.risk_score
    assert payload["breach_status"] == assessment.breach_status.value
    assert payload["target"] == assessment.target.model_dump(mode="json")
    assert assessment.human_review_required is True


def test_agent_workflows_work_in_mock_and_mock_mcp() -> None:
    mock = run_agent("SYN-CANCER-2WW-001", ExecutionMode.MOCK)
    mock_mcp = run_agent("SYN-CANCER-2WW-001", ExecutionMode.MOCK_MCP)

    assert mock.execution_mode == ExecutionMode.MOCK
    assert mock_mcp.execution_mode == ExecutionMode.MOCK_MCP
    assert mock_mcp.human_review_required is True


def test_live_mode_is_not_available_through_public_service() -> None:
    with pytest.raises(DomainValidationError):
        run_agent("SYN-CANCER-2WW-001", ExecutionMode.LIVE)


def test_evidence_and_guardrails_are_controlled() -> None:
    assessment = run_deterministic("SYN-CANCER-2WW-001")
    evidence = get_evidence("SYN-CANCER-2WW-001", 5)
    guardrails = get_guardrail_result(assessment)

    assert evidence
    assert all(item.demonstration_only and item.validation_required for item in evidence)
    assert guardrails.passed is True


def test_human_review_approve_amend_reject_and_integrity(tmp_path: Path) -> None:
    config = config_for(tmp_path)
    approved = prepare_review("SYN-CANCER-2WW-001", ExecutionMode.MOCK_MCP, config)
    assert approved.status.value == "PENDING"

    approved = decide_review(
        approved.review_id,
        HumanReviewDecision.APPROVE,
        "demo-reviewer",
        config,
        comments="Approved for demonstration",
    )
    assert approved.status.value == "APPROVED_FOR_DEMONSTRATION"
    assert approved.submitted is False
    assert approved.authenticated_identity is False

    amended = prepare_review("SYN-CANCER-2WW-001", ExecutionMode.MOCK_MCP, config)
    amended = decide_review(
        amended.review_id,
        HumanReviewDecision.AMEND,
        "demo-reviewer",
        config,
        reason="Clarify narrative",
        amendment_field="case_summary",
        amendment_value="Clarify synthetic wording",
    )
    assert amended.status.value == "AMENDMENT_REQUIRED"
    assert amended.amendments[0].field == "case_summary"

    rejected = prepare_review("SYN-CANCER-2WW-001", ExecutionMode.MOCK_MCP, config)
    rejected = decide_review(
        rejected.review_id,
        HumanReviewDecision.REJECT,
        "demo-reviewer",
        config,
        reason="Not suitable for demonstration",
    )
    assert rejected.status.value == "REJECTED"


def test_review_requires_alias_and_rejects_immutable_amendments(tmp_path: Path) -> None:
    config = config_for(tmp_path)
    record = prepare_review("SYN-CANCER-2WW-001", ExecutionMode.MOCK_MCP, config)

    with pytest.raises(DomainValidationError):
        decide_review(record.review_id, HumanReviewDecision.APPROVE, "", config)
    with pytest.raises(DomainValidationError):
        decide_review(
            record.review_id,
            HumanReviewDecision.AMEND,
            "demo-reviewer",
            config,
            reason="Bad change",
            amendment_field="risk_score",
            amendment_value="10",
        )


def test_evaluation_evidence_and_metrics_load() -> None:
    evidence = load_evaluation_evidence()

    assert evidence["benchmark"]["case_count"] == 30
    assert evidence["benchmark"]["overall_pass_rate"] == 1.0
    assert any(row["metric"] == "deterministic_preservation_rate" for row in evidence["metrics"])
    assert "synthetic" in evidence["limitations"].lower()


def test_architecture_and_limitations_content_loads() -> None:
    assert "Agents" in ARCHITECTURE_SUMMARY
    assert any("Synthetic data only" in item for item in LIMITATIONS)


def test_downloads_are_safe_json_and_reject_path_traversal() -> None:
    assessment = run_deterministic("SYN-CANCER-2WW-001")
    data = build_download(assessment, "assessment")

    assert b'"demonstration_only": true' in data
    assert b'"human_review_required": true' in data
    with pytest.raises(DomainValidationError):
        build_download(assessment, "../assessment")


def test_path_traversal_case_id_is_rejected() -> None:
    with pytest.raises(DomainValidationError):
        get_case_summary("../secret")


def test_safe_errors_do_not_expose_paths_or_stack_traces() -> None:
    message = concise_error(RuntimeError('Traceback File "/Users/example/.env" api_key=secret'))

    assert "Traceback" not in message
    assert "/Users/" not in message
    assert "secret" not in message


def test_session_state_resets_on_case_change() -> None:
    state = {"selected_case_id": "A", "agent_result": object(), "review_id": "R"}

    reset_case_state(state, "B")

    assert state["selected_case_id"] == "B"
    assert "agent_result" not in state
    assert "review_id" not in state


def test_health_check_works_without_gemini(tmp_path: Path) -> None:
    health = run_health_checks(config_for(tmp_path))

    assert health["status"] == "healthy"
    assert health["agent_execution_mode"] == "mock-mcp"
    assert health["live_mode_enabled"] is False


class FakeColumn:
    """Tiny Streamlit column fake."""

    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def metric(self, label: str, value: object) -> None:
        self.calls.append(f"metric:{label}:{value}")


class FakeStreamlit:
    """Tiny Streamlit fake for component rendering."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def title(self, value: str) -> None:
        self.calls.append(f"title:{value}")

    def caption(self, value: str) -> None:
        self.calls.append(f"caption:{value}")

    def warning(self, value: str) -> None:
        self.calls.append(f"warning:{value}")

    def info(self, value: str) -> None:
        self.calls.append(f"info:{value}")

    def write(self, *values: object) -> None:
        self.calls.append("write:" + " ".join(str(value) for value in values))

    def subheader(self, value: str) -> None:
        self.calls.append(f"subheader:{value}")

    def json(self, value: object) -> None:
        self.calls.append(f"json:{type(value).__name__}")

    def columns(self, count: int) -> list[FakeColumn]:
        self.calls.append(f"columns:{count}")
        return [FakeColumn(self.calls) for _ in range(count)]

    def dataframe(self, value: object, hide_index: bool = False) -> None:
        self.calls.append(f"dataframe:{hide_index}:{type(value).__name__}")

    def markdown(self, value: str) -> None:
        self.calls.append(f"markdown:{len(value)}")


def test_streamlit_components_render_with_safe_fixed_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = FakeStreamlit()
    monkeypatch.setattr(components, "st", fake)
    assessment = run_deterministic("SYN-CANCER-2WW-001")
    agent = run_agent("SYN-CANCER-2WW-001", ExecutionMode.MOCK_MCP)
    evidence = get_evidence("SYN-CANCER-2WW-001", 5)
    guardrails = get_guardrail_result(assessment, agent)
    evaluation = load_evaluation_evidence()

    components.render_header("Title", "Subtitle")
    components.render_case(get_case_summary("SYN-CANCER-2WW-001"))
    components.render_assessment(assessment)
    components.render_agent(agent)
    components.render_evidence(evidence)
    components.render_guardrails(guardrails)
    components.render_evaluation(evaluation)
    components.render_architecture_and_limitations()

    assert any(call.startswith("warning:") for call in fake.calls)
    assert any("Deterministic Assessment" in call for call in fake.calls)
    assert any("Agent Workflow" in call for call in fake.calls)
    assert any("Evaluation Evidence" in call for call in fake.calls)


def test_review_component_renders_review_record(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = FakeStreamlit()
    monkeypatch.setattr(components, "st", fake)
    record = prepare_review("SYN-CANCER-2WW-001", ExecutionMode.MOCK_MCP, config_for(tmp_path))

    components.render_review(record)

    assert any("Human Review Record" in call for call in fake.calls)
    assert any(call.startswith("dataframe:") for call in fake.calls)
