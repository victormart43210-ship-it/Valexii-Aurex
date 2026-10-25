FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY integrations/kusanagi-xvi/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /app/backend /app/sovereign_intake /data && useradd --uid 10001 --create-home aurex
COPY integrations/kusanagi-xvi/backend/*.py ./backend/
COPY integrations/sovereign_intake/sovereign_intake/*.py ./sovereign_intake/
# Railway mounts /data as root at container start, after image build.
# PID 1 boot owns only this volume path and drops to uid 10001 before
# launching the API + optional worker/observer. No root-lived app process.
USER root
CMD ["python", "-m", "backend.boot"]
