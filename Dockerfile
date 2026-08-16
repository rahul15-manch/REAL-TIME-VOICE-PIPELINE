FROM python:3.14.4-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies
# libsndfile1 is required by the soundfile python package for audio processing
RUN apt-get update && \
    apt-get install -y --no-install-recommends libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Run as non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose the application port
EXPOSE 8000

# Start the application using Gunicorn with Uvicorn workers
# We use 4 workers to support horizontal scaling across CPU cores,
# as the application natively handles distributed locking via PostgreSQL.
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--workers", "4", "--bind", "0.0.0.0:8000", "app.main:app"]
