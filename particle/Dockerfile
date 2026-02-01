FROM python:3.11-slim

# Install build dependencies for tree-sitter
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install package
RUN pip install -e .

# Set environment
ENV PYTHONPATH=/app/src

# Default command
ENTRYPOINT ["collider"]
CMD ["--help"]
