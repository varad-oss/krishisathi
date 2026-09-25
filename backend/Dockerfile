# Production-ready Python 3.11 image
FROM python:3.11-slim

# Prevent writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r krishisathi && useradd -r -g krishisathi krishisathi

WORKDIR /app

# Install dependencies (only required)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set ownership
RUN chown -R krishisathi:krishisathi /app

# Drop root privileges
USER krishisathi

# Expose production port
EXPOSE 8000

# Health check using the exact path we implemented
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/live || exit 1

# Run Uvicorn with concurrency limits and production settings
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--log-level", "info", "--timeout-keep-alive", "65"]
