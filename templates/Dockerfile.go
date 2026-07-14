# Production Dockerfile for a Go service (build context = the service dir, e.g. api/common).
# ---- build ----
FROM golang:1.26-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o app .

# ---- runtime ----
FROM alpine:latest
RUN adduser -D -u 10001 appuser
WORKDIR /app
COPY --from=builder /app/app .
USER appuser
# Honor $PORT (Cloud Run); the app should default to 8080 locally.
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- "http://localhost:${PORT:-8080}/health" || exit 1
CMD ["./app"]
