FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY aurex/ ./aurex/
COPY training/ ./training/
COPY workstation/ ./workstation/
RUN python -m pip --isolated install --no-cache-dir --index-url https://pypi.org/simple pip==26.2.1
RUN python -m pip --isolated install --no-cache-dir --index-url https://pypi.org/simple . \
    && useradd --uid 10001 --create-home --shell /usr/sbin/nologin aurex \
    && mkdir -p /data \
    && chown 10001:10001 /data
RUN chmod -R a+rX /app/aurex /app/training /app/workstation
USER 10001:10001
EXPOSE 8080
CMD ["sh", "-c", "exec uvicorn aurex.api:app --host 0.0.0.0 --port ${PORT:-8080} --no-access-log"]
