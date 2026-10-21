FROM python:3.13-alpine AS builder

RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    git

WORKDIR /build

COPY pyproject.toml .

RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /wheels .

FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # Use stdio transport for Docker as the default. Revisit after streamable-http
    MCP_TRANSPORT=stdio \
    LOG_LEVEL=INFO \
    OPENAPI_SPEC_PATH=/app/openapi.json

WORKDIR /app

# The python base image lags Alpine security releases, and CI reuses cached layers,
# so bump APK_SECURITY_REFRESH to pull the latest Alpine packages again.
# 2026-10-21: ca-certificates 20261020-r0 drops emSign ECC Root CA - G3, whose
# subordinate CA keys are compromised.
ARG APK_SECURITY_REFRESH=2026-10-21
RUN echo "apk security refresh: $APK_SECURITY_REFRESH" \
    && apk upgrade --no-cache \
    && apk add --no-cache git

# Copy wheels from builder and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && \
    rm -rf /wheels

COPY src/ ./src/
COPY server.py .
COPY swagger.json /app/openapi.json

RUN adduser -D -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

ENTRYPOINT ["python", "server.py"]
