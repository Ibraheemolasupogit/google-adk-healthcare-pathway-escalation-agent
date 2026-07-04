# Cloud Run Readiness

This project is ready to be packaged for Cloud Run as a synthetic Streamlit demonstration. This milestone does not deploy automatically.

## Build

```bash
docker build -f deployment/Dockerfile -t healthcare-pathway-agent:local .
```

For Google Artifact Registry, tag the image with your own registry path. Do not commit real project IDs or credentials.

## Run Locally

```bash
docker run --rm -p 8080:8080 -e PORT=8080 healthcare-pathway-agent:local
```

The app reads `PORT`, runs Streamlit headlessly and defaults to `APP_DEFAULT_EXECUTION_MODE=mock-mcp`.

## Cloud Run Settings

- Container port: `8080`
- Environment: `APP_DEFAULT_EXECUTION_MODE=mock-mcp`
- Environment: `APP_ENABLE_LIVE_MODE=false`
- Runtime review path: `artifacts/ui-reviews` or another writable container path
- Public access: only for synthetic demonstration deployments
- Authenticated access: recommended for non-public review or internal demos

## Secrets

No Gemini key is required for the default public demo. If live mode is ever enabled, use Google Secret Manager or workload identity. Do not put secrets in environment examples, source files, Docker layers or Streamlit session state.

## Limitations

Cloud Run readiness is packaging readiness only. Actual deployment, domain configuration, IAM, monitoring, audit logging, VPC settings, production review identity and governance approval are out of scope for Milestone 7.

