FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml ./

RUN uv sync

COPY . .

EXPOSE 8000