# Docker Usage (ARM64)

This project is Python + Selenium. The container is configured for **linux/arm64** and uses **Chromium + chromedriver** (ARM-compatible) instead of Microsoft Edge.

## Build

```bash
docker build --platform linux/arm64 -t autorewarder:arm64 .
```

## Run

### Show CLI options

```bash
docker run --rm --platform linux/arm64 autorewarder:arm64 --help
```

### Typical headless run

```bash
docker run --rm \
  --platform linux/arm64 \
  -v autorewarder_data:/root/.local/share/AutoRewarder \
  autorewarder:arm64 \
  --account "Main" --pc 30 --mobile 20
```

### Compose

```bash
docker compose up --build
```

Adjust `command:` in `docker-compose.yml` to your desired CLI arguments.

## Environment variables

- `AUTOREWARDER_BROWSER=chromium` (required in container)
- `CHROME_BIN=/usr/bin/chromium`
- `CHROMEDRIVER_PATH=/usr/bin/chromedriver`
- `TZ=UTC` (optional)

Runtime data is stored in `/root/.local/share/AutoRewarder` (mapped to `autorewarder_data` volume in Compose).

## ARM64 notes

- Base image: `python:3.12-slim-bookworm` (multi-arch).
- Browser stack uses Debian ARM64 packages (`chromium`, `chromium-driver`) to avoid amd64-only binaries.
- On non-ARM hosts, use Buildx/QEMU emulation for `--platform linux/arm64` builds.

## Known limitation

The app automates Microsoft Rewards accounts and requires account setup/login state in the persistent profile volume before meaningful runs.
