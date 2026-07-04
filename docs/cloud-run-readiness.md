# Cloud Run Readiness

Cloud Run readiness is documented in `deployment/cloud-run.md`.

Implemented readiness items:

- Streamlit listens on `PORT`.
- Container uses a small supported Python base image.
- Container runs as a non-root user.
- `.dockerignore` excludes credentials, `.env`, `.git`, caches and artifacts.
- Default execution mode is `mock-mcp`.
- Live mode is disabled by default.
- No Gemini credentials are required for the public demonstration.
- `scripts/verify_deployment.py` validates local readiness without network calls.

Not completed:

- Actual Cloud Run deployment.
- IAM setup.
- Domain mapping.
- Production monitoring.
- Authenticated reviewer identity.
- Live Gemini validation.

