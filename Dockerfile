# Build stage for Go scheduler (optional)
FROM golang:1.21-alpine AS go-builder

WORKDIR /build
COPY go.mod ./ 2>/dev/null || true
RUN if [ -f go.mod ]; then go mod download; fi

COPY cmds/scheduler/ ./ 2>/dev/null || true
RUN if [ -f main.go ]; then CGO_ENABLED=0 go build -o scheduler .; fi

# Main stage
FROM python:3.11-slim

# Install SQLite
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY src/ ./src/
COPY ai-scraper.yaml ./

# Copy Go scheduler binary if built
COPY --from=go-builder /build/scheduler /usr/local/bin/scheduler 2>/dev/null || true

# Create data and output directories
RUN mkdir -p /app/data /app/output /app/.cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV AI_SCRAPER_DATA_DIR=/app/data
ENV AI_SCRAPER_OUTPUT_DIR=/app/output

# Entry point
ENTRYPOINT ["python", "-m", "ai_scraper.cli"]
CMD ["--help"]
