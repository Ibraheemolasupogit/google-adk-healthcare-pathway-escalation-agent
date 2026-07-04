"""Schemas for local MCP interoperability and reusable Agent Skills."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, StrictBool

from schemas.agent import ExecutionMode


class MCPTransport(StrEnum):
    """Allowed local MCP transports."""

    STDIO = "stdio"
    IN_MEMORY = "in-memory"


class MCPServerDefinition(BaseModel):
    """Static allow-listed MCP server definition."""

    name: str
    transport: MCPTransport
    entry_point: str
    approved_tools: list[str]
    approved_resources: list[str]
    timeout_seconds: float = Field(gt=0)
    maximum_calls: int = Field(gt=0)
    enabled_modes: list[ExecutionMode]


class MCPToolDescriptor(BaseModel):
    """MCP tool descriptor exposed by the local registry."""

    server_name: str
    tool_name: str
    description: str


class MCPResourceDescriptor(BaseModel):
    """MCP resource descriptor exposed by the local registry."""

    server_name: str
    resource_uri: str
    description: str


class MCPInvocation(BaseModel):
    """Auditable MCP invocation request."""

    server_name: str
    capability_name: str
    capability_type: str
    input_summary: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime


class MCPInvocationResult(BaseModel):
    """Auditable MCP invocation result."""

    invocation: MCPInvocation
    output_summary: dict[str, Any] = Field(default_factory=dict)
    completed_at: datetime
    duration_ms: float = Field(ge=0)
    success: StrictBool
    error: str | None = None


class SkillDefinition(BaseModel):
    """Approved reusable local Agent Skill definition."""

    name: str
    version: str
    description: str
    input_schema_path: str
    output_schema_path: str
    dependencies: list[str]
    demonstration_only: StrictBool = True
    human_review_required: StrictBool = True


class SkillExecutionRequest(BaseModel):
    """Request to execute an approved local Agent Skill."""

    request_id: str
    skill_name: str
    case_id: str
    execution_mode: ExecutionMode = ExecutionMode.MOCK_MCP


class SkillExecutionStep(BaseModel):
    """Auditable skill execution step."""

    sequence: int = Field(ge=1)
    skill_name: str
    description: str
    started_at: datetime
    completed_at: datetime
    success: StrictBool


class SkillValidationResult(BaseModel):
    """Skill validation result."""

    valid: StrictBool
    findings: list[str] = Field(default_factory=list)


class SkillExecutionResult(BaseModel):
    """Structured skill execution result."""

    request_id: str
    execution_mode: ExecutionMode
    skill_name: str
    skill_version: str
    case_id: str
    output: dict[str, Any]
    steps: list[SkillExecutionStep]
    mcp_invocations: list[MCPInvocationResult]
    validation: SkillValidationResult
    warnings: list[str]
    demonstration_only: StrictBool = True
    human_review_required: StrictBool = True
    success: StrictBool
