# Multi-stage Docker build for Spectrometer API
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Create non-root user
RUN groupadd -r spectrometer && useradd -r -g spectrometer spectrometer

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create app directory
WORKDIR /app

# Copy application code
COPY spectrometer_v9_raw_haiku.py .
COPY spectrometer_api_rest.py .

# Create necessary directories
RUN mkdir -p uploads temp logs

# Change ownership
RUN chown -R spectrometer:spectrometer /app

# Switch to non-root user
USER spectrometer

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')" || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "spectrometer_api_rest:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]