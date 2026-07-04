# Tool Access Matrix

| Agent | Approved MCP Access |
| --- | --- |
| Coordinator Agent | `case-data.get_case`, `case-data.validate_case`, `pathway-rules.run_pathway_assessment` |
| Pathway Agent | `pathway-rules.get_pathway_rule`, `pathway-rules.calculate_elapsed_time`, `pathway-rules.determine_breach_status` |
| Risk Agent | `pathway-rules.run_pathway_assessment` |
| Evidence Agent | `policy-evidence.search_evidence`, `policy-evidence.get_evidence`, `policy-evidence.get_evidence_for_pathway` |
| Escalation Agent | Consumes validated outputs only |
| Review Agent | Validates outputs and audit summaries only |
