# Production Dockerfile for a Go service (build context = the service dir, e.g. api/common).
# ---- build ----
FROM golang:1.26-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
# Entrypoint per the standard layout (cmd/server/main.go).
RUN CGO_ENABLED=0 go build -o app ./cmd/server

# ---- runtime ----
FROM alpine:3.20
RUN apk add --no-cache ca-certificates && adduser -D -u 10001 appuser
WORKDIR /app
COPY --from=builder /app/app .
USER appuser
# Honor $PORT (Cloud Run); the app should default to 8080 locally.
# EXPOSE is metadata only — when adapting this template for an additional API
# (8081, 8082, … per the port convention), set EXPOSE to that service's port.
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- "http://localhost:${PORT:-8080}/health" || exit 1
CMD ["./app"]
