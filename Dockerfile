# Multi-stage Dockerfile for Contact Reconciliation Service
# Stage 1: Builder - Install dependencies
FROM python:3.12-slim as builder

# Set working directory for builder stage
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies with latest pip
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final - Runtime image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application code to /app/app/
COPY app/ ./app/

# Set environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app/app
ENV DATABASE_URL=sqlite:///contacts.db

# Expose port 8000
EXPOSE 8000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Initialize database and start the application
CMD ["sh", "-c", "cd /app/app && python init_db.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
