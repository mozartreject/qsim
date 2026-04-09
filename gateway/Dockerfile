# =============================================================================
# Gateway Dockerfile
# Save as: qsim/gateway/Dockerfile
# ARM64-native, slim Python base, production-ready
# =============================================================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching — only rebuilds if requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create data directory (will be overridden by PVC mount in Kubernetes)
RUN mkdir -p /data

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app /data
USER appuser

# Expose port
EXPOSE 8000

# Health check baked into image
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Production entrypoint — single worker for demo (increase for prod)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
