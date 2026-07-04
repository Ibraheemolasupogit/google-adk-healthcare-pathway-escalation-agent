# Deployment

Milestone 7 adds a Cloud Run-ready Streamlit container for a synthetic public demonstration.

The image defaults to `mock-mcp`, requires no Gemini credentials and does not connect to live NHS systems.

## Local Container Build

```bash
docker build -f deployment/Dockerfile -t healthcare-pathway-agent:local .
```

## Local Container Run

```bash
docker run --rm -p 8080:8080 -e PORT=8080 healthcare-pathway-agent:local
```

Then open `http://localhost:8080`.

## Verification

```bash
python3 scripts/verify_deployment.py
```

This checks imports, synthetic data, mock-MCP execution, committed evaluation evidence, Docker configuration and review-store writability without calling Gemini.

Do not bake `.env`, service-account keys, credentials or runtime artifacts into the image.

