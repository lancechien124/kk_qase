# Multi-stage build for MeterSphere Python Backend

# Stage 1: Builder stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
# Build context is parent directory (metersphere/), so requirements.txt is at root
COPY requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Create non-root user
RUN useradd -m -u 1000 metersphere && \
    mkdir -p /app/backend_python/logs /app/backend_python/uploads /opt/metersphere/logs/metersphere && \
    chown -R metersphere:metersphere /app /opt/metersphere

# Copy application code (from backend_python directory)
COPY backend_python/ ./backend_python/
WORKDIR /app/backend_python

# Switch to non-root user
USER metersphere

# Expose port
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8081/api/v1/health/live || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081", "--workers", "4"]
