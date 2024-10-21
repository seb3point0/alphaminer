FROM python:3.11-slim

ENV PROJECT_NAME=${PROJECT_NAME}
ENV WEB_PORT=${WEB_PORT}

WORKDIR /app

RUN apt-get -y update \
    && apt-get -y install curl \
    && rm -rf /var/lib/apt/lists/*

COPY poetry.lock /app
COPY pyproject.toml /app

RUN pip install --no-cache-dir poetry==1.8.1

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev \
    && pip install --no-cache-dir uvicorn==0.32.0

COPY ./app /app

HEALTHCHECK CMD curl --fail http://0.0.0.0:${WEB_PORT}/health || exit 1
