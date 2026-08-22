FROM node:24-bookworm-slim AS web-builder
WORKDIR /build/apps/web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    H29C_SERVE_FRONTEND=true \
    H29C_DATABASE_PATH=/app/var/handover29c.sqlite3 \
    H29C_BUILD_LABEL=container
WORKDIR /app
COPY apps/api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && addgroup --system handover29c \
    && adduser --system --ingroup handover29c --home /nonexistent handover29c \
    && mkdir -p /app/var \
    && chown handover29c:handover29c /app/var
COPY apps/api/ /app/apps/api/
COPY fixtures/ /app/fixtures/
COPY --from=web-builder /build/apps/web/dist/ /app/apps/web/dist/
USER handover29c
WORKDIR /app/apps/api
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=4s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"]
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
