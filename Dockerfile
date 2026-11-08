FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY aurex/ ./aurex/
COPY aurex_foundation/ ./aurex_foundation/
COPY training/ ./training/
COPY workstation/ ./workstation/
COPY docker/entrypoint.py /entrypoint.py
COPY tools/verify_xaeli_private_qwen.py /app/tools/verify_xaeli_private_qwen.py
RUN pip install --no-cache-dir . \
    && useradd --uid 10001 --create-home --shell /usr/sbin/nologin aurex \
    && mkdir -p /data /app/tools \
    && chown 10001:10001 /data \
    && chmod 755 /entrypoint.py
USER root
EXPOSE 8080
ENTRYPOINT ["python", "/entrypoint.py"]
