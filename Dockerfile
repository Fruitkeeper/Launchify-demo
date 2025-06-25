# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Set Python path to include project root
ENV PYTHONPATH=/app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Default command
CMD ["python", "run/run.py", "--help"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sqlite3; sqlite3.connect('/app/data.db').close()" || exit 1

# Labels for metadata
LABEL maintainer="Meta-Agent LLM Router"
LABEL description="Intelligent LLM routing system with self-learning feedback loop"
LABEL version="1.0"

# Volume for persistent data
VOLUME ["/app/data"]

# Expose port if adding web interface later
EXPOSE 8000 