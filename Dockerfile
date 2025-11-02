# Dockerfile for deployment
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src ./src

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose port (Render/Railway use $PORT env var)
EXPOSE 8000

# Run the application
CMD uvicorn src.webapp.main:app --host 0.0.0.0 --port ${PORT:-8000}
