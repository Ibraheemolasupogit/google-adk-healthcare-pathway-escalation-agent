# Agent Instructions

Agent instructions are stored under `agents/instructions/`.

Shared safety rules:

- use only supplied evidence;
- treat deterministic values as authoritative;
- do not invent missing data;
- do not provide clinical advice;
- do not expose secrets;
- do not bypass human review;
- distinguish evidence from inference;
- clearly mark demonstration-only content;
- do not claim operational readiness for real NHS use.

The review agent's positive result means only that the draft is safe to present to an authorised human reviewer. It does not mean the escalation is operationally or clinically approved.
