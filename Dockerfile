# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip wheel --wheel-dir /wheels .

FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="Huawei Cloud FinOps Optimizer" \
      org.opencontainers.image.description="Explainable cloud cost and capacity optimization API" \
      org.opencontainers.image.source="https://github.com/muratmiracg-dev/Huawei-Cloud-FinOps---Intelligent-Capacity-Optimization" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FINOPS_DATA_DIR=/app/data/demo

RUN groupadd --gid 10001 finops \
    && useradd --uid 10001 --gid finops --no-create-home --shell /usr/sbin/nologin finops

WORKDIR /app
COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels
COPY --chown=finops:finops data/demo ./data/demo

USER 10001:10001
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health/live', timeout=2)"

CMD ["uvicorn", "finops.api:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2", "--no-access-log"]
