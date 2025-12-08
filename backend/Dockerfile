# Multi-stage build for optimization
# Using python:3.11 (full Debian) for better ML library compatibility
# Alternative: python:3.11-slim (smaller but may need more system libs)
FROM python:3.11 as builder

WORKDIR /app

# Install build dependencies (minimal but complete)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU-only first (much smaller than full PyTorch)
# This reduces sentence-transformers dependencies significantly
RUN pip install --no-cache-dir --user \
    torch==2.1.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
# Using python:3.11 (full Debian) for maximum compatibility
# Size: ~900MB base vs ~150MB for slim, but much better ML library support
FROM python:3.11

WORKDIR /app

# Install runtime dependencies (minimal but compatible)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy ONLY application code (exclude data, tests, etc.)
COPY api/ ./api/
COPY rag_system/ ./rag_system/
COPY main.py .

# Create cache directory for models (downloaded at runtime, not in image)
RUN mkdir -p /root/.cache/huggingface && \
    chmod 755 /root/.cache/huggingface

# Remove unnecessary files to reduce size
# CRITICAL: DO NOT remove .dist-info directories - they contain package metadata
# required by importlib.metadata for runtime package detection
RUN find /root/.local -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /root/.local -type f -name "*.pyc" -delete 2>/dev/null || true && \
    find /root/.local -type f -name "*.pyo" -delete 2>/dev/null || true && \
    find /root/.local -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /root/.local -type d -name "test" -exec rm -rf {} + 2>/dev/null || true && \
    find /root/.local -type f -name "*.txt" ! -name "METADATA" ! -name "RECORD" -delete 2>/dev/null || true && \
    find /root/.local -type f -name "*.md" -delete 2>/dev/null || true && \
    find /root/.local -type f -name "*.rst" -delete 2>/dev/null || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Use gunicorn with uvicorn workers
CMD ["gunicorn", "main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120", "--graceful-timeout", "30"]
