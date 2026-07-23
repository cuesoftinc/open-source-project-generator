## Ecosystem API conventions

- Versioned base path `/api/v1` (products) — upstat's public surfaces use
  `/v1` (events/stats/query are cross-product infrastructure).
- Error envelope `{"error": {"code", "message", "details?"}}`; codes are
  **snake_case and stable**, owned by the flow docs (never invented in code
  review). Cross-tenant access returns `404`, never `403`.
- Cursor pagination (`?cursor=&limit=`, default 50).
- `Idempotency-Key` header on any client-retryable mutation (uploads,
  payments, submissions) — retries must never duplicate.
- Rate limits per engineering.md; `429` + `Retry-After`.
- Auth: Firebase ID-token bearer (Google-only); machine identities
  (service tokens, property keys) never grant user-API access.

## Telemetry standard (OpenTelemetry, X-9)

Every service instruments with **OTel SDKs**: traces (auto-instrumentation
for HTTP/gRPC/DB clients + manual spans on domain operations), custom
metrics (Meter API: counters/histograms per service KPIs), logs (slog/logging
bridges). W3C `traceparent` propagates across all service boundaries.
Export = **direct OTLP from the SDK** (BatchSpan/LogRecord processors);
collector sidecar = later upgrade path, never a v1 requirement. **Receiver =
upstat's OTLP gateway** (4317 gRPC / 4318 HTTP, ingest-key header; sibling
exporters default to OTLP/HTTP — only upstat hosts the ecosystem OTLP
receiver, X-8) — CueLABS™
products dogfood upstat for their own observability. Export is env-gated:
no OTEL_EXPORTER_OTLP_ENDPOINT → SDK no-ops (pre-OBS-001 posture). JSON
stdout logging remains alongside (Cloud Run native). Operational telemetry
≠ product analytics events (upstat /v1/events) — separate pipelines, never
mixed. Env: OTEL_SERVICE_NAME, OTEL_EXPORTER_OTLP_ENDPOINT,
OTEL_EXPORTER_OTLP_HEADERS, OTEL_RESOURCE_ATTRIBUTES.

## Environment-variable naming standard

Identical names across all repos (Doppler `<project>/stg` is the source of
values; `.env.example` documents names with dev-safe defaults):
`PORT` · `CORS_ORIGINS` (comma-separated exact origins — the only CORS var;
never ALLOWED_ORIGINS/FRONTEND_URL) · `REDIS_HOST/PORT/USERNAME/PASSWORD/TLS/DB`
(discrete, irealty pattern) · `BREVO_API_KEY/FROM_EMAIL/FROM_NAME` ·
`GOOGLE_CLOUD_PROJECT` · `SERVICE_TOKEN_HASH` (server side of s2s token
validation) · DB: `MONGO_URI`+`MONGO_DB` (Mongo era) / `DATABASE_URL`
(Postgres era) / ADC for Firestore. CORS behaviour contract lives in each
repo's engineering.md ("CORS contract" section).

