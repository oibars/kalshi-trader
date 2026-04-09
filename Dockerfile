# Kalshi Trader - Railway Deployment
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn pydantic httpx structlog

EXPOSE 8002

CMD ["uvicorn", "kalshi_trader.app:app", "--host", "0.0.0.0", "--port", "8002"]