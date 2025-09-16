# Multi-stage Dockerfile for Open Source Template Generator

# Build stage
FROM golang:1.25-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates

# Set working directory
WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the binary
ARG VERSION="dev"
ARG GIT_COMMIT="unknown"
ARG BUILD_TIME="unknown"

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags="-w -s -X main.Version=${VERSION} -X main.GitCommit=${GIT_COMMIT} -X main.BuildTime=${BUILD_TIME}" \
    -o generator ./cmd/generator

# Final stage
FROM alpine:latest

# Install runtime dependencies
RUN apk --no-cache add ca-certificates

# Create non-root user
RUN addgroup -g 1000 generator && \
    adduser -D -u 1000 -G generator generator

# Create workspace directory
RUN mkdir -p /workspace && \
    chown -R generator:generator /workspace

# Copy binary from builder stage
COPY --from=builder /app/generator /usr/local/bin/generator

# Copy templates
COPY --chown=generator:generator templates/ /usr/share/generator/templates/

# Set permissions
RUN chmod +x /usr/local/bin/generator

# Switch to non-root user
USER generator

# Set working directory
WORKDIR /workspace

# Set environment variables
ENV GENERATOR_TEMPLATES_DIR=/usr/share/generator/templates

# Default command
ENTRYPOINT ["generator"]
CMD ["--help"]