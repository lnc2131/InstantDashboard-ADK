FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy poetry files first
COPY pyproject.toml poetry.lock ./

# Copy README.md for Poetry package mode
COPY README.md ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Install dependencies only (not the package itself)
RUN poetry install --only=main --no-root

# Copy application code
COPY . .

# Expose port
EXPOSE $PORT

# Start command
CMD poetry run uvicorn api.main:app --host 0.0.0.0 --port $PORT 