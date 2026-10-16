FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AUREX_DB_PATH=/data/aurex_jobs.db

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 10001 aurex && \
    useradd -u 10001 -g aurex -s /bin/bash -m aurex && \
    mkdir -p /data /app && \
    chown -R aurex:aurex /data /app

COPY pyproject.toml /app/
COPY aurex /app/aurex
COPY scripts /app/scripts

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

USER aurex

EXPOSE 8000

CMD ["sh", "-c", "uvicorn aurex.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
