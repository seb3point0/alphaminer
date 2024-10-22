FROM python:3.11-slim

# Environment variables
ENV PROJECT_NAME=${PROJECT_NAME}
ENV WEB_PORT=${WEB_PORT}

# Create a non-root user and group
RUN groupadd -g 1001 appuser \
    && useradd -m -u 1001 -g appuser -s /bin/bash appuser

# Set working directory
WORKDIR /app

# Install dependencies as root
RUN apt-get -y update \
    && apt-get -y install curl \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry files
COPY poetry.lock pyproject.toml /app/

# Install Poetry and dependencies as root
RUN pip install --no-cache-dir poetry==1.8.1 \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev \
    && pip install --no-cache-dir uvicorn==0.32.0

# Copy the rest of the app's code
COPY ./app /app

# Change ownership of /app to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser
