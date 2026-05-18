# syntax=docker/dockerfile:1.7
FROM --platform=$TARGETPLATFORM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive \
    AUTOREWARDER_BROWSER=chromium \
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    HOME=/home/app \
    APP_DATA_DIR=/home/app/.local/share/AutoRewarder

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium chromium-driver xvfb fluxbox x11vnc novnc websockify \
    ca-certificates fonts-liberation libnss3 libatk-bridge2.0-0 libgtk-3-0 libgbm1 libasound2 tzdata curl \
  && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 -s /bin/bash app
WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
RUN chmod +x docker/entrypoint.sh && chown -R app:app /app /home/app

USER app
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["web"]
