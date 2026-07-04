"""Google ADK orchestration service for Milestone 3."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, TypeVar, cast
from uuid import uuid4

from agents.registry import build_agent_registry
from mcp_servers.client import BoundedMCPClient
from pydantic import ValidationError
from schemas.agent import (
    AgentDraft,
    AgentExecutionResult,
    AgentName,
    AgentRequest,
    AgentStep,
    AgentToolInvocation,
    ExecutionMode,
    LocalEvidenceDocument,
    ReviewFinding,
    ReviewResult,
    ReviewSeverity,
)
from schemas.assessment import PathwayAssessment, ReviewStatus
from tools.case_tools import get_case_by_id
from tools.evidence_tools import retrieve_local_evidence
from tools.exceptions import DomainValidationError
from tools.pathway_tools import get_pathway_rule

from services.agent_config import (
    AgentRuntimeConfig,
    load_agent_runtime_config,
    validate_live_configuration,
)
from services.agent_review import review_agent_draft
from services.guardrail_service import GuardrailService

MAX_WORKFLOW_STEPS = 12
MAX_TOOL_CALLS = 16
MAX_INPUT_SIZE = 4000
T = TypeVar("T")


class AgentOrchestrationError(RuntimeError):
    """Raised when the agent orchestration workflow fails safely."""


class AgentOrchestrator:
    """Coordinate ADK agent definitions and deterministic tools."""

    def __init__(self, config: AgentRuntimeConfig | None = None) -> None:
        self.config = config or load_agent_runtime_config(ExecutionMode.MOCK)
        self.agents = build_agent_registry()
        self.steps: list[AgentStep] = []
        self.tool_invocations: list[AgentToolInvocation] = []

    def run(self, request: AgentRequest) -> AgentExecutionResult:
        """Run a bounded agent workflow and return a validated execution result."""
        if request.execution_mode == ExecutionMode.LIVE:
            validate_live_configuration(load_agent_runtime_config(ExecutionMode.LIVE))
            raise DomainValidationError(
                "Live Gemini execution is configured but not invoked by automated tests. "
                "Use this mode only in an environment where external model calls are intended."
            )
        if request.execution_mode == ExecutionMode.DETERMINISTIC:
            raise DomainValidationError("Use assess-case for deterministic mode without agents.")
        self._validate_request(request)

        mcp_client = (
            BoundedMCPClient() if request.execution_mode == ExecutionMode.MOCK_MCP else None
        )

        if request.case is not None:
            case = request.case
        elif mcp_client is not None:
            case_payload = mcp_client.call_tool(
                "case-data",
                "get_case",
                {"case_id": request.case_id},
            )
            case = get_case_by_id(case_payload["case"]["case_id"])
        else:
            case = self._invoke_tool(
                AgentName.COORDINATOR,
                "get_synthetic_case",
                {"case_id": request.case_id},
                lambda: get_case_by_id(str(request.case_id)),
            )
        self._record_step(
            AgentName.COORDINATOR,
            "Validated synthetic case request and selected specialist workflow.",
            f"case_id={case.case_id}",
            "case validated",
        )

        if mcp_client is not None:
            rule_payload = mcp_client.call_tool(
                "pathway-rules",
                "get_pathway_rule",
                {"pathway_code": case.pathway_code.value},
            )
            rule = get_pathway_rule(case.pathway_code)
            assessment_payload = mcp_client.call_tool(
                "pathway-rules",
                "run_pathway_assessment",
                {"case_id": case.case_id},
            )
            assessment = PathwayAssessment.model_validate(assessment_payload["assessment"])
            self.tool_invocations.extend(_mcp_to_agent_invocations(mcp_client))
            mcp_invocation_count = len(mcp_client.invocations)
            _ = rule_payload
        else:
            rule = self._invoke_tool(
                AgentName.PATHWAY,
                "get_pathway_rule",
                {"pathway_code": case.pathway_code.value},
                lambda: get_pathway_rule(case.pathway_code),
            )
            assessment = self._invoke_tool(
                AgentName.PATHWAY,
                "run_deterministic_assessment",
                {"case_id": case.case_id},
                lambda: __import__(
                    "services.assessment_service", fromlist=["assess_case"]
                ).assess_case(case),
            )
        self._record_step(
            AgentName.PATHWAY,
            "Retrieved pathway rule and deterministic breach status.",
            rule.pathway_code.value,
            assessment.breach_status.value,
        )

        risk_factors = self._invoke_tool(
            AgentName.RISK,
            "get_risk_factors",
            {"case_id": case.case_id},
            lambda: assessment.risk_factors,
        )
        self._record_step(
            AgentName.RISK,
            "Preserved deterministic risk score and explained contributing factors.",
            f"risk_score={assessment.risk_score}",
            f"{len(risk_factors)} factors",
        )

        if mcp_client is not None:
            evidence_payload = mcp_client.call_tool(
                "policy-evidence",
                "get_evidence_for_pathway",
                {"pathway_code": case.pathway_code.value},
            )
            evidence = [
                LocalEvidenceDocument.model_validate(item) for item in evidence_payload["evidence"]
            ]
            self.tool_invocations.extend(
                _renumber_invocations(
                    _mcp_to_agent_invocations(mcp_client)[mcp_invocation_count:],
                    start_sequence=len(self.tool_invocations) + 1,
                )
            )
        else:
            evidence = self._invoke_tool(
                AgentName.EVIDENCE,
                "retrieve_local_evidence",
                {"pathway_code": case.pathway_code.value},
                lambda: retrieve_local_evidence(case.pathway_code),
            )
        self._record_step(
            AgentName.EVIDENCE,
            "Retrieved local demonstration evidence.",
            case.pathway_code.value,
            f"{len(evidence)} evidence document(s)",
        )

        draft = self._build_mock_draft(assessment, evidence)
        self._record_step(
            AgentName.ESCALATION,
            "Generated structured non-clinical operational draft.",
            assessment.case_id,
            "draft generated",
        )

        review_result = review_agent_draft(draft.model_dump(mode="json"), assessment)
        guardrail_result = GuardrailService().check_draft(draft, assessment)
        if not guardrail_result.safe_for_human_review:
            guardrail_findings = [
                ReviewFinding(
                    finding_code=finding.category.value,
                    severity=ReviewSeverity.ERROR,
                    message=finding.message,
                    field=finding.field,
                )
                for finding in guardrail_result.findings
            ]
            review_result = ReviewResult(
                safe_for_human_review=False,
                findings=[*review_result.findings, *guardrail_findings],
                validation_passed=False,
                prohibited_language_detected=review_result.prohibited_language_detected,
                unsupported_claims_detected=True,
                review_status=ReviewStatus.PENDING,
            )
        self._record_step(
            AgentName.REVIEW,
            "Validated draft for safe presentation to a human reviewer.",
            assessment.case_id,
            f"safe_for_human_review={review_result.safe_for_human_review}",
        )

        result = AgentExecutionResult(
            request_id=request.request_id,
            case_id=assessment.case_id,
            deterministic_assessment=assessment,
            agent_draft=draft,
            review_result=review_result,
            agent_steps=self.steps,
            tool_invocations=self.tool_invocations,
            warnings=[*assessment.warnings, "Mock mode used no Gemini call."],
            demonstration_only=True,
            human_review_required=True,
            review_status=ReviewStatus.PENDING,
            audit_trace_id=assessment.audit_trace_id,
            model_metadata={
                "mode": request.execution_mode.value,
                "model_provider": (
                    "mock-mcp"
                    if request.execution_mode == ExecutionMode.MOCK_MCP
                    else "mock"
                    if request.execution_mode == ExecutionMode.MOCK
                    else "none"
                ),
                "google_adk_version": load_agent_runtime_config(
                    request.execution_mode
                ).google_adk_version,
                "model_name": "mock-local-adapter",
            },
            execution_mode=request.execution_mode,
        )
        return AgentExecutionResult.model_validate(result.model_dump())

    def _validate_request(self, request: AgentRequest) -> None:
        text_size = len(request.model_dump_json())
        if text_size > MAX_INPUT_SIZE:
            raise DomainValidationError("agent request exceeds maximum input size")
        if request.case_id is None and request.case is None:
            raise DomainValidationError("agent request requires case_id or structured case")

    def _record_step(
        self,
        agent_name: AgentName,
        responsibility: str,
        input_summary: str,
        output_summary: str,
    ) -> None:
        if len(self.steps) >= MAX_WORKFLOW_STEPS:
            raise AgentOrchestrationError("maximum workflow step limit exceeded")
        now = datetime.now(UTC)
        self.steps.append(
            AgentStep(
                sequence=len(self.steps) + 1,
                agent_name=agent_name,
                responsibility=responsibility,
                input_summary=input_summary[:200],
                output_summary=output_summary[:200],
                started_at=now,
                completed_at=now,
            )
        )

    def _invoke_tool(
        self,
        agent_name: AgentName,
        tool_name: str,
        inputs: dict[str, object],
        func: Callable[[], T],
    ) -> T:
        if len(self.tool_invocations) >= MAX_TOOL_CALLS:
            raise AgentOrchestrationError("maximum tool-call limit exceeded")
        started_at = datetime.now(UTC)
        try:
            output = func()
            success = True
            output_summary = _summarise_output(output)
        except Exception as exc:
            success = False
            output_summary = {"error": str(exc)}
            raise
        finally:
            completed_at = datetime.now(UTC)
            self.tool_invocations.append(
                AgentToolInvocation(
                    sequence=len(self.tool_invocations) + 1,
                    agent_name=agent_name,
                    tool_name=tool_name,
                    input_summary=_redact(inputs),
                    output_summary=output_summary if "output_summary" in locals() else {},
                    started_at=started_at,
                    completed_at=completed_at,
                    success=success if "success" in locals() else False,
                )
            )
        return output

    def _build_mock_draft(
        self,
        assessment: PathwayAssessment,
        evidence: list[LocalEvidenceDocument],
    ) -> AgentDraft:
        factor_text = "; ".join(
            f"{factor.factor_code}: {factor.score_contribution}"
            for factor in assessment.risk_factors
        )
        action_text = "; ".join(action.description for action in assessment.recommended_actions)
        evidence_text = "; ".join(f"{doc.evidence_id}: {doc.title}" for doc in evidence)
        sections = {
            "Case Summary": f"Synthetic case {assessment.case_id} on {assessment.pathway_name}.",
            "Pathway Status": (
                f"{assessment.breach_status.value}; elapsed {assessment.elapsed_time.value} "
                f"{assessment.elapsed_time.unit.value}; target {assessment.target.value} "
                f"{assessment.target.unit.value}."
            ),
            "Operational Risk": (
                f"Risk score {assessment.risk_score}; level {assessment.risk_level.value}."
            ),
            "Deterministic Risk Factors": factor_text,
            "Supporting Demonstration Evidence": evidence_text,
            "Recommended Operational Actions": action_text,
            "Assumptions": "; ".join(assessment.assumptions),
            "Warnings": "; ".join(assessment.warnings),
            "Human Review Status": "Human review is required; review status is pending.",
            "Audit Trace": f"Audit trace ID {assessment.audit_trace_id}.",
        }
        return AgentDraft(
            case_id=assessment.case_id,
            sections=sections,
            deterministic_values={
                "breach_status": assessment.breach_status.value,
                "risk_score": assessment.risk_score,
                "risk_level": assessment.risk_level.value,
                "target_value": assessment.target.value,
                "elapsed_value": assessment.elapsed_time.value,
            },
            evidence=evidence,
            unsupported_claims=[],
            demonstration_only=True,
            human_review_required=True,
            review_status=ReviewStatus.PENDING,
        )


def run_agent_assessment(
    case_id: str,
    mode: ExecutionMode = ExecutionMode.MOCK,
) -> AgentExecutionResult:
    """Run agent orchestration for a synthetic case ID."""
    request = AgentRequest(
        request_id=f"REQ-{uuid4()}",
        case_id=case_id,
        execution_mode=mode,
    )
    return AgentOrchestrator(load_agent_runtime_config(mode)).run(request)


def validate_agent_configuration(mode: ExecutionMode = ExecutionMode.MOCK) -> dict[str, object]:
    """Return safe non-secret configuration status for agent orchestration."""
    config = load_agent_runtime_config(mode)
    if mode == ExecutionMode.LIVE:
        validate_live_configuration(config)
    return {
        "google_adk_version": config.google_adk_version,
        "execution_mode": mode.value,
        "model_name": config.model_name,
        "live_ready": config.live_ready,
        "api_key_configured": config.google_api_key_configured,
        "vertex_project_configured": config.google_cloud_project_configured,
        "vertex_location_configured": config.google_cloud_location_configured,
    }


def _redact(inputs: dict[str, object]) -> dict[str, object]:
    redacted: dict[str, object] = {}
    for key, value in inputs.items():
        if "key" in key.lower() or "token" in key.lower() or "secret" in key.lower():
            redacted[key] = "<redacted>"
        else:
            redacted[key] = value
    return redacted


def _summarise_output(output: object) -> dict[str, object]:
    if hasattr(output, "case_id"):
        value = cast(Any, output)
        return {"case_id": value.case_id}
    if hasattr(output, "pathway_code"):
        value = cast(Any, output)
        return {"pathway_code": value.pathway_code.value}
    if isinstance(output, list):
        return {"items": len(output)}
    return {"type": type(output).__name__}


def _mcp_to_agent_invocations(client: BoundedMCPClient) -> list[AgentToolInvocation]:
    converted: list[AgentToolInvocation] = []
    for item in client.invocations:
        converted.append(
            AgentToolInvocation(
                sequence=len(converted) + 1,
                agent_name=_agent_for_server(item.invocation.server_name),
                tool_name=f"mcp:{item.invocation.server_name}.{item.invocation.capability_name}",
                input_summary=item.invocation.input_summary,
                output_summary=item.output_summary,
                started_at=item.invocation.started_at,
                completed_at=item.completed_at,
                success=item.success,
            )
        )
    return converted


def _renumber_invocations(
    invocations: list[AgentToolInvocation], start_sequence: int
) -> list[AgentToolInvocation]:
    return [
        invocation.model_copy(update={"sequence": start_sequence + offset})
        for offset, invocation in enumerate(invocations)
    ]


def _agent_for_server(server_name: str) -> AgentName:
    if server_name == "case-data":
        return AgentName.COORDINATOR
    if server_name == "pathway-rules":
        return AgentName.PATHWAY
    if server_name == "policy-evidence":
        return AgentName.EVIDENCE
    return AgentName.REVIEW


def validate_malformed_model_output(payload: dict[str, object]) -> ReviewResult:
    """Validate malformed model output safely for tests and callers."""
    try:
        assessment = PathwayAssessment.model_validate(payload.get("deterministic_assessment"))
    except (ValidationError, TypeError):
        return ReviewResult(
            safe_for_human_review=False,
            findings=[],
            validation_passed=False,
            prohibited_language_detected=False,
            unsupported_claims_detected=True,
            review_status=ReviewStatus.PENDING,
        )
    draft_payload = payload.get("agent_draft", {})
    if not isinstance(draft_payload, dict):
        draft_payload = {}
    return review_agent_draft(dict(draft_payload), assessment)
