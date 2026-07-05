# Video Recording Plan

## Browser and Terminal Preparation

- Close unrelated windows and tabs.
- Use a clean browser profile if possible.
- Set browser zoom to 90 percent or 100 percent.
- Recommended window size: 1440 x 900.
- Keep terminal visible only for startup and validation, with no local paths or secrets shown in the final recording.

## Presentation Mode Startup

```bash
DEMO_PRESENTATION_MODE=true streamlit run ui/streamlit_app.py
```

If the console script is unavailable:

```bash
DEMO_PRESENTATION_MODE=true python3 -m streamlit run ui/streamlit_app.py
```

Use a custom port only if the default Streamlit port is already in use.

## Tabs to Open

1. Overview
2. Select Case
3. Deterministic Assessment
4. Agent Workflow
5. Evidence
6. Security and Guardrails
7. Human Review
8. Evaluation Evidence
9. Architecture and Limitations

## Order of Actions

1. Start Streamlit in presentation mode.
2. Confirm selected case is `SYN-CANCER-62-003`.
3. Show safety banner and badges.
4. Run deterministic assessment.
5. Run agent workflow in `mock-mcp`.
6. Show evidence.
7. Show guardrails.
8. Prepare review and apply a demonstration decision.
9. Show evaluation evidence.
10. End on limitations and conclusion.

## Expected Outputs

- Case ID: `SYN-CANCER-62-003`.
- Execution mode: `mock-mcp`.
- Breach status: `BREACHED`.
- Risk score: `7.5`.
- Risk level: `CRITICAL`.
- Review record starts as `PENDING`.
- Final review record remains `submitted=false` and `authenticated_identity=false`.

## Recovery Plan

- If Streamlit fails to start, run `python3 scripts/verify_deployment.py`.
- If a review record is already decided, prepare a new review record.
- If the UI becomes cluttered, refresh the browser and rerun the deterministic and agent steps.
- If a command fails, do not hide the failure. Explain that this is a local demo and switch to CLI output if needed.

## Recording Checklist

- Safety banner visible.
- No secrets visible.
- No local absolute paths visible.
- No unsupported clinical or deployment claims.
- Video under 5 minutes.
- `mock-mcp` mode visible.

## Audio Checklist

- Use a quiet room.
- Speak slowly enough to explain limitations.
- Avoid saying "Gemini generated this" for mock or mock-MCP output.
- Avoid saying "approved by NHS" or "production ready."

## Post-Recording Checklist

- Confirm duration under 5 minutes.
- Confirm audio is clear.
- Confirm no credentials, local paths or private windows are visible.
- Upload manually as public or unlisted only when ready.
- Add the YouTube URL to Kaggle only after upload.

