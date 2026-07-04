# MCP Security Model

The MCP layer uses static allow-lists, local-only server entry points, schema validation, input and output size limits, maximum call limits, path traversal rejection, safe redaction and structured failure states.

The client does not accept arbitrary server URLs or arbitrary tool names. Evidence text is treated as untrusted data rather than instructions.
