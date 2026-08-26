FROM node:24-bookworm-slim AS web-builder
WORKDIR /build/apps/web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    IR_SERVE_FRONTEND=true \
    IR_BUILD_LABEL=container
WORKDIR /app
COPY apps/api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && addgroup --system identityrescue \
    && adduser --system --ingroup identityrescue --home /nonexistent identityrescue
COPY apps/api/ /app/apps/api/
COPY --from=web-builder /build/apps/web/dist/ /app/apps/web/dist/
USER identityrescue
WORKDIR /app/apps/api
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=4s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"]
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
