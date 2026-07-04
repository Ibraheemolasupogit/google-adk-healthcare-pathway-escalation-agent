"""Schemas for Milestone 6 deterministic evaluation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, StrictBool


class EvaluationMetric(BaseModel):
    """One named evaluation metric."""

    name: str
    value: float
    threshold: float | None = None
    passed: StrictBool = True


class EvaluationFailure(BaseModel):
    """One evaluation failure."""

    case_id: str
    check_name: str
    expected: Any = None
    actual: Any = None
    message: str


class EvaluationCaseResult(BaseModel):
    """Result for one evaluated case."""

    case_id: str
    passed: StrictBool
    metrics: list[EvaluationMetric] = Field(default_factory=list)
    failures: list[EvaluationFailure] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class EvaluationSuiteResult(BaseModel):
    """Common result shape for an evaluation suite."""

    evaluation_id: str
    evaluator_version: str
    benchmark_version: str
    started_at: datetime
    completed_at: datetime
    case_count: int
    passed_count: int
    failed_count: int
    skipped_count: int
    pass_rate: float
    metrics: list[EvaluationMetric]
    failures: list[EvaluationFailure]
    warnings: list[str]
    execution_mode: str
    demonstration_only: StrictBool
    checksums: dict[str, str]
    reproducibility_metadata: dict[str, Any] = Field(default_factory=dict)


class DeterministicEvaluationResult(EvaluationSuiteResult):
    """Deterministic assessment evaluation result."""


class AgentEvaluationResult(EvaluationSuiteResult):
    """Agent orchestration evaluation result."""


class SkillEvaluationResult(EvaluationSuiteResult):
    """Agent Skill evaluation result."""


class EvidenceGroundingResult(EvaluationSuiteResult):
    """Evidence grounding evaluation result."""


class ReviewEvaluationResult(EvaluationSuiteResult):
    """Human-review evaluation result."""


class ReproducibilityResult(EvaluationSuiteResult):
    """Reproducibility evaluation result."""


class EvaluationManifest(BaseModel):
    """Benchmark manifest schema."""

    benchmark_version: str
    created_date: str
    schema_version: str
    supported_pathways: list[str]
    case_count: int
    case_distribution: dict[str, int]
    expected_output_checksums: dict[str, str]
    rule_data_checksum: str
    evidence_data_checksum: str
    evaluator_version: str
    demonstration_only: StrictBool
    reproducibility_notes: list[str]


class EvaluationReport(BaseModel):
    """Full evaluation report."""

    run_id: str
    manifest: EvaluationManifest
    deterministic: DeterministicEvaluationResult
    agent_mock: AgentEvaluationResult
    agent_mock_mcp: AgentEvaluationResult
    execution_mode_parity: EvaluationSuiteResult
    skills: SkillEvaluationResult
    evidence: EvidenceGroundingResult
    security: dict[str, Any]
    review: ReviewEvaluationResult
    reproducibility: ReproducibilityResult
    overall_pass_rate: float
    failed_case_ids: list[str]
    demonstration_only: StrictBool = True
