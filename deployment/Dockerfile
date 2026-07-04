FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_DEFAULT_EXECUTION_MODE=mock-mcp
ENV APP_ENABLE_LIVE_MODE=false
ENV APP_ENVIRONMENT_LABEL=cloud-run-ready-demo
ENV STREAMLIT_SERVER_PORT=8080

WORKDIR /app

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY requirements.txt pyproject.toml README.md LICENSE ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY agents ./agents
COPY data ./data
COPY docs ./docs
COPY evaluation ./evaluation
COPY mcp_servers ./mcp_servers
COPY schemas ./schemas
COPY scripts ./scripts
COPY security ./security
COPY services ./services
COPY tools ./tools
COPY ui ./ui

RUN mkdir -p /app/artifacts/ui-reviews \
    && chown -R appuser:appgroup /app/artifacts

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python scripts/verify_deployment.py || exit 1

CMD ["sh", "-c", "streamlit run ui/streamlit_app.py --server.address=0.0.0.0 --server.port=${PORT:-8080} --server.headless=true --browser.gatherUsageStats=false"]
