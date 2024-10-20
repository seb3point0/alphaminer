ARG PROJECT_NAME
ARG WEB_PORT=8000  # Default port if not provided during build

FROM python:3.11-slim

ENV PROJECT_NAME=${PROJECT_NAME}
ENV WEB_PORT=${WEB_PORT}

WORKDIR /${PROJECT_NAME}

COPY pyproject.toml poetry.lock /${PROJECT_NAME}/

RUN pip install poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

COPY ./app /${PROJECT_NAME}/app

# Expose a default port or use the one passed via the build argument
EXPOSE ${WEB_PORT}

# Use shell form to ensure environment variable expansion
CMD uvicorn app.main:app --host 0.0.0.0 --port $WEB_PORT --reload