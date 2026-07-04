# MCP Architecture

Milestone 4 implements three local MCP-compatible servers using `mcp` 1.28.1 and `FastMCP`: Case Data, Pathway Rules and Policy Evidence.

The selected server transport is local stdio. Automated tests and CLI demonstrations use a bounded in-memory adapter that calls the same approved handlers without exposing a public port.

MCP is an interoperability boundary, not a replacement for the deterministic domain layer.

Milestone 6 uses mock-MCP evaluation to verify that agent execution through the bounded adapter preserves deterministic assessment fields and retrieves only controlled local evidence.

Milestone 7 uses `mock-mcp` as the default UI execution mode so the public demonstration exercises the MCP boundary without Gemini credentials or network calls.
