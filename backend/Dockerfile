# Backend Dockerfile for BIZIT Organism
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc git && rm -rf /var/lib/apt/lists/*

# Install Common Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install redis uvicorn fastapi  # Ensure these are present

# Copy Source Code
COPY backend /app/backend
COPY config.template.yaml /app/config.yaml

# Create non-root user
RUN useradd -m bizit
USER bizit

# Environment Variables
ENV PYTHONPATH=/app/backend
ENV USE_REDIS=true
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

# Entrypoint script (default to main loop, override for API)
CMD ["python", "backend/main_loop.py"]
