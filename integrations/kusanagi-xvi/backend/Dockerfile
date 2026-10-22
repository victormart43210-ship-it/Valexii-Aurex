FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /app/backend /data && useradd --uid 10001 --create-home aurex && chown aurex:aurex /data
COPY *.py ./backend/
USER aurex
CMD ["python", "-m", "backend.supervisor"]
