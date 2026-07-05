# Demo Commands

## Environment Installation

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
make install
```

## Project Validation

```bash
python3 scripts/validate_project.py
python3 scripts/verify_deployment.py
python3 scripts/final_submission_check.py
```

## Deterministic Demo

```bash
python3 -m app.main assess-case --case-id SYN-CANCER-62-003 --json
```

## Mock Agent Demo

```bash
python3 -m app.main agent-assess --case-id SYN-CANCER-62-003 --mode mock --json
```

## Mock-MCP Demo

```bash
python3 -m app.main agent-assess --case-id SYN-CANCER-62-003 --mode mock-mcp --json
```

## Security Evaluation

```bash
python3 -m app.main run-security-evaluation
```

## Full Evaluation

```bash
python3 -m app.main run-full-evaluation
```

## Streamlit UI

```bash
streamlit run ui/streamlit_app.py
```

If the console script is unavailable:

```bash
python3 -m streamlit run ui/streamlit_app.py
```

## Presentation Mode

```bash
DEMO_PRESENTATION_MODE=true streamlit run ui/streamlit_app.py
```

If the console script is unavailable:

```bash
DEMO_PRESENTATION_MODE=true python3 -m streamlit run ui/streamlit_app.py
```

## Deployment Verification

```bash
python3 scripts/verify_deployment.py
```

No command requires real credentials for the default public demonstration.

