# Use official Python 3.10 image (Debian Bookworm based)
FROM python:3.10-slim

# Install system dependencies
# We use the modern 'signed-by' method for the Google Cloud SDK as apt-key is deprecated
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && apt-get update && apt-get install -y google-cloud-sdk \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
# We use the one in standard-model-of-code as it's the most complete
COPY standard-model-of-code/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy essential bootstrap files
COPY cloud-entrypoint.sh /app/
COPY context-management/tools/ai/analyze.py /app/context-management/tools/ai/
COPY context-management/config/ /app/context-management/config/

# Make entrypoint executable
RUN chmod +x /app/cloud-entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PROJECT_ROOT=/app/repo_mirror

# Default command: Sync and Run
ENTRYPOINT ["/app/cloud-entrypoint.sh"]
